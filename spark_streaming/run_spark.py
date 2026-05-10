import os
import sys
import logging # check error
from typing import Optional, List, Dict, Any # for type hint
from colorama import Fore, Style, init # for color output
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, TimestampType
from pyspark.sql.dataframe import DataFrame

class Background_colors:
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    MAGENTA = "\033[45m"
    CYAN = "\033[46m"
    END = "\033[0m"

VERBOSE = True # show log message

LOG_FILE = os.environ.get("LOG_FILE", "logs/run_spark.log")
MINIO_BUCKET = os.environ.get("MINIO_BUCKET", "music-events")
CHECKPOINT_PATH = os.environ.get("CHECKPOINT_PATH", "checkpoints/music-events")
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "http://localhost:9050")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# setup log file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=LOG_FILE,
                    filemode="a")
logger = logging.getLogger("spark_streaming")

# print message with color
def verbose_output(message: str) -> None:
    if VERBOSE:
        print(f"{message}{Background_colors.END}")

# create spark session
def create_spark_session() -> SparkSession:
    try:
        spark = SparkSession.builder \
            .appName("SparkStreamingToMinIO") \
            .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3") \
            .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT) \
            .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
            .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
            .config("spark.hadoop.fs.s3a.path.style.access", "true") \
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
            .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
            .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
            .getOrCreate()
        
        spark.sparkContext.setLogLevel("ERROR")
        verbose_output(
            f"{Background_colors.GREEN} Create Spark Session Sucesssfully"
        )
        logger.info("Spark session created successfully for MinIO")
    except Exception as e:
        verbose_output(
            f"{Background_colors.RED} Couldn't create the spark session: {e}"
        )
        logger.error(f"Couldn't create the spark session: {e}")
        sys.exit(1)

    return spark

# connect to kafka to get messages
def connect_to_kafka(spark_conn: SparkSession) -> Optional[DataFrame]:
    spark_df = None
    try:
        spark_df = spark_conn.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
            .option("subscribe", "music_events") \
            .option("startingOffsets", "earliest") \
            .option("maxOffsetsPerTrigger", 5000) \
            .option("failOnDataLoss", "false") \
            .load()
        logger.info("Connected to Kafka successfully")
        verbose_output(
            f"{Background_colors.GREEN} Connect to Kafka successfully"
        )
    except Exception as e:
        verbose_output(
            f"{Background_colors.RED} Couldn't connect to Kafka: {e}"
        )
        logger.error(f"Couldn't connect to Kafka: {e}")
        sys.exit(1)
    return spark_df # raw binary data from kafka

# define schema of json data
def get_event_schema() -> StructType:
    return StructType([
        StructField("ts", StringType(), True), # change to string to handle Datatime by DBT and avoid error when checking data with ClickHouse
        StructField("userId", StringType(), True),
        StructField("sessionId", IntegerType(), True),
        StructField("page", StringType(), True),
        StructField("auth", StringType(), True),
        StructField("method", StringType(), True),
        StructField("status", IntegerType(), True),
        StructField("level", StringType(), True),
        StructField("itemInSession", IntegerType(), True),
        StructField("location", StringType(), True),
        StructField("userAgent", StringType(), True),
        StructField("lastName", StringType(), True),
        StructField("firstName", StringType(), True),
        StructField("registration", StringType(), True), # change to string to handle Datatime by DBT
        StructField("gender", StringType(), True),
        StructField("artist", StringType(), True),
        StructField("song", StringType(), True),
        StructField("length", FloatType(), True),
    ])

# convert raw binary data to json data
def get_json_data(raw_df: DataFrame, schema: StructType) -> Optional[DataFrame]: 
    try:
        json_df = raw_df.selectExpr("CAST(value AS STRING)") \
            .select(from_json(col("value"), schema).alias("data")) \
            .select("data.*")
        logger.info("JSON data extracted successfully")
        verbose_output(
            f"{Background_colors.GREEN} JSON data extracted successfully"
        )
    except Exception as e:
        verbose_output(
            f"{Background_colors.RED} Couldn't extract JSON data: {e}"
        )
        logger.error(f"Couldn't extract JSON data: {e}")
        sys.exit(1)
    return json_df

# display messages of a micro-batch to console
def display_data(df: DataFrame):
    try:
        df.writeStream \
            .format("console") \
            .outputMode("append") \
            .option("truncate", "false") \
            .option("numRows", "500") \
            .start()
        # show full table and max 500 rows
        logger.info("Data displayed successfully")
        verbose_output(
            f"{Background_colors.GREEN} Data displayed successfully"
        )
    except Exception as e:
        verbose_output(
            f"{Background_colors.RED} Couldn't display data: {e}"
        )
        logger.error(f"Couldn't display data: {e}")
        sys.exit(1)

# push data to minio
def write_to_minio(df: DataFrame, bucket_name: str, checkpoint_path: str): # write data to minio
    try:
        df.writeStream \
            .format("parquet") \
            .outputMode("append") \
            .trigger(processingTime='1 minute') \
            .option("checkpointLocation", checkpoint_path) \
            .option("path", f"s3a://{bucket_name}/data") \
            .start()
        logger.info("Data written to MinIO successfully")
        verbose_output(
            f"{Background_colors.GREEN} Data written to MinIO successfully"
        )
    except Exception as e:
        verbose_output(
            f"{Background_colors.RED} Couldn't write data to MinIO: {e}"
        )
        logger.error(f"Couldn't write data to MinIO: {e}")
        sys.exit(1)

# connect to kafka -> convert to json -> display -> write to minio
def main():
    spark = create_spark_session()
    raw_df = connect_to_kafka(spark)
    json_df = get_json_data(raw_df, get_event_schema())
    display_data(json_df)
    write_to_minio(json_df, MINIO_BUCKET, CHECKPOINT_PATH)
    spark.streams.awaitAnyTermination() # keep spark running

if __name__ == "__main__":
    main()