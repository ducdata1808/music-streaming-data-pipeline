import os
import sys
import logging
from colorama import Fore, Style, init

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, struct, row_number
from pyspark.sql.window import Window
from pyspark.ml.recommendation import ALS
from pyspark.ml.feature import StringIndexer, IndexToString
from pyspark.ml import Pipeline

class Background_colors:
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    MAGENTA = "\033[45m"
    CYAN = "\033[46m"
    END = "\033[0m"

VERBOSE = True

# Environment variables to support both local and docker-compose execution
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_LOG_FILE = os.path.join(_APP_DIR, "..", "logs", "run_als.log")
os.makedirs(os.path.dirname(_DEFAULT_LOG_FILE), exist_ok=True)

LOG_FILE = os.environ.get("LOG_FILE", _DEFAULT_LOG_FILE)
MINIO_BUCKET = os.environ.get("MINIO_BUCKET", "music-events")
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "http://localhost:9050")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
CLICKHOUSE_HOST = os.environ.get("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = os.environ.get("CLICKHOUSE_PORT", "8123")
CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "")

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=LOG_FILE,
                    filemode="a")
logger = logging.getLogger("spark_als")

def verbose_output(message: str) -> None:
    if VERBOSE:
        print(f"{message}{Background_colors.END}")

def create_spark_session() -> SparkSession:
    try:
        # Added clickhouse-jdbc to packages
        spark = SparkSession.builder \
            .appName("SparkALS_Recommendations") \
            .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262,com.clickhouse:clickhouse-jdbc:0.4.6") \
            .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT) \
            .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
            .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
            .config("spark.hadoop.fs.s3a.path.style.access", "true") \
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
            .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
            .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
            .getOrCreate()
        
        spark.sparkContext.setLogLevel("ERROR")
        verbose_output(f"{Background_colors.GREEN} Create Spark Session Successfully")
        logger.info("Spark session created successfully for ALS")
        return spark
    except Exception as e:
        verbose_output(f"{Background_colors.RED} Couldn't create the spark session: {e}")
        logger.error(f"Couldn't create the spark session: {e}")
        sys.exit(1)

def main():
    spark = create_spark_session()
    
    # 1. Read input data from ClickHouse
    verbose_output(f"{Background_colors.CYAN} Reading mart_user_play_counts from ClickHouse at {CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}...")
    jdbc_url = f"jdbc:clickhouse://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/music_analytics"
    
    try:
        df = spark.read \
            .format("jdbc") \
            .option("url", jdbc_url) \
            .option("user", CLICKHOUSE_USER) \
            .option("password", CLICKHOUSE_PASSWORD) \
            .option("dbtable", "mart_user_play_counts") \
            .option("driver", "com.clickhouse.jdbc.ClickHouseDriver") \
            .load()
        
        row_count = df.count()
        verbose_output(f"{Background_colors.GREEN} Successfully read {row_count} rows from ClickHouse")
        logger.info(f"Read {row_count} rows from mart_user_play_counts")
        
        if row_count < 100:
            verbose_output(f"{Background_colors.YELLOW} WARNING: Not enough data ({row_count} rows) to train a meaningful ALS model. Continuing anyway...")
            
    except Exception as e:
        verbose_output(f"{Background_colors.RED} Failed to read from ClickHouse: {e}")
        logger.error(f"Failed to read from ClickHouse: {e}")
        sys.exit(1)

    # 2. Encode string columns to integer indices
    verbose_output(f"{Background_colors.CYAN} Encoding user and song strings to indices...")
    user_indexer = StringIndexer(inputCol="user_id", outputCol="user_idx", handleInvalid="skip")
    song_indexer = StringIndexer(inputCol="song", outputCol="song_idx", handleInvalid="skip")
    
    pipeline = Pipeline(stages=[user_indexer, song_indexer])
    pipeline_model = pipeline.fit(df)
    df_encoded = pipeline_model.transform(df)

    # Convert play_count to float for ALS
    df_encoded = df_encoded.withColumn("play_count", col("play_count").cast("float"))

    # 3. Train ALS model
    verbose_output(f"{Background_colors.CYAN} Training ALS model...")
    als = ALS(
        userCol="user_idx",
        itemCol="song_idx",
        ratingCol="play_count",
        implicitPrefs=True,       # Implicit feedback
        coldStartStrategy="drop", # Ignore users/songs with no history
        rank=50,                  # Number of latent factors
        maxIter=10,
        regParam=0.1
    )
    
    try:
        model = als.fit(df_encoded)
        verbose_output(f"{Background_colors.GREEN} ALS model trained successfully")
    except Exception as e:
        verbose_output(f"{Background_colors.RED} Failed to train ALS model: {e}")
        logger.error(f"Failed to train ALS model: {e}")
        sys.exit(1)

    # 4. Generate top 10 recommendations for all users
    verbose_output(f"{Background_colors.CYAN} Generating top 10 recommendations for all users...")
    try:
        user_recs = model.recommendForAllUsers(10)
        # Explode the recommendations array to individual rows
        user_recs_exploded = user_recs.select(
            col("user_idx"), 
            explode(col("recommendations")).alias("rec")
        ).select(
            col("user_idx"),
            col("rec.song_idx").alias("song_idx"),
            col("rec.rating").alias("score")
        )
    except Exception as e:
         verbose_output(f"{Background_colors.RED} Failed to generate recommendations: {e}")
         logger.error(f"Failed to generate recommendations: {e}")
         sys.exit(1)

    # 5. Decode integer indices back to original string values
    verbose_output(f"{Background_colors.CYAN} Decoding indices back to original strings...")
    
    user_converter = IndexToString(inputCol="user_idx", outputCol="user_id", labels=pipeline_model.stages[0].labels)
    song_converter = IndexToString(inputCol="song_idx", outputCol="song", labels=pipeline_model.stages[1].labels)
    
    recs_decoded_users = user_converter.transform(user_recs_exploded)
    recs_decoded_all = song_converter.transform(recs_decoded_users)

    # Join back with original df to get the artist name for each song
    song_artist_map = df.select("song", "artist").distinct()
    final_recs = recs_decoded_all.join(song_artist_map, on="song", how="left")
    
    # Add a rec_rank column using window function
    windowSpec = Window.partitionBy("user_id").orderBy(col("score").desc())
    final_recs = final_recs.withColumn("rec_rank", row_number().over(windowSpec))
    
    # Select final columns to save
    final_output = final_recs.select("user_id", "rec_rank", "song", "artist", "score")

    # 6. Write to MinIO as Parquet
    minio_path = f"s3a://{MINIO_BUCKET}/recommendations"
    verbose_output(f"{Background_colors.CYAN} Writing recommendations to MinIO at {minio_path}...")
    
    try:
        final_output.write \
            .mode("overwrite") \
            .parquet(minio_path)
        verbose_output(f"{Background_colors.GREEN} Recommendations successfully written to MinIO")
        logger.info("Recommendations successfully written to MinIO")
    except Exception as e:
        verbose_output(f"{Background_colors.RED} Failed to write to MinIO: {e}")
        logger.error(f"Failed to write to MinIO: {e}")
        sys.exit(1)
        
    spark.stop()
    verbose_output(f"{Background_colors.GREEN} ALS Job Completed Successfully!{Background_colors.END}")

if __name__ == "__main__":
    main()
