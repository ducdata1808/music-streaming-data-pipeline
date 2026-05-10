from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.python import PythonOperator
from airflow_clickhouse_plugin.operators.clickhouse import ClickHouseOperator
from airflow.utils.dates import days_ago # used to set start date
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig # used to run dbt
from cosmos.profiles import ClickhouseUserPasswordProfileMapping # used to set dbt profile
from datetime import timedelta # used to set retry delay
from clickhouse_driver import Client # used to interact with clickhouse
import boto3 # used to interact with AWS services
from datetime import datetime, timedelta
import os

# Parameters
SPARK_APP_PATH = os.environ.get("SPARK_APP_PATH", "/opt/airflow/spark_streaming/run_spark.py")
ALS_APP_PATH = os.environ.get("ALS_APP_PATH", "/opt/airflow/spark_streaming/run_als.py")
MINIO_BUCKET = os.environ.get("MINIO_BUCKET", "music-events")
DBT_PROJECT_DIR = os.environ.get("DBT_PROJECT_DIR", "/opt/airflow/dbt")
DBT_PROFILE_NAME = os.environ.get("DBT_PROFILE_NAME", "music_events_transform")
MINIO_ENDPOINT_URL = os.environ.get("MINIO_ENDPOINT", "http://localhost:9050")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
CLICKHOUSE_HOST = os.environ.get("CLICKHOUSE_HOST", "localhost")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='music_events_pipeline',
    start_date=days_ago(1),
    schedule_interval='@daily',
    default_args=default_args,
    catchup=False,
    tags=['music_events'],
)


#task 1: run spark manual

# task 2: check data in MinIO
def check_new_files_in_minio(**context):
    s3 = boto3.client(
        's3',
        endpoint_url=MINIO_ENDPOINT_URL,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )
    # get data in 24 hours (to avoid race condition with Spark micro-batch flush)
    cutoff = datetime.utcnow() - timedelta(hours=24)
    # Prefix='data' matches Spark's path s3a://music-events/data (no trailing slash)
    response = s3.list_objects_v2(Bucket='music-events', Prefix='data')
    all_files = response.get('Contents', [])
    print(f"[check_minio] total files in bucket: {len(all_files)}")
    for obj in all_files:
        print(f"  - {obj['Key']} | Size: {obj.get('Size', 0)} bytes | LastModified: {obj['LastModified']}")
    new_files = [
        obj for obj in all_files
        if obj['LastModified'].replace(tzinfo=None) >= cutoff and obj['Key'].endswith('.parquet')
    ]
    print(f"[check_minio] found {len(new_files)} new files in last 24 hours")
    if len(new_files) == 0:
        raise ValueError("No new files in MinIO in the last 24h — Spark not writing data!")

check_minio = PythonOperator(
    task_id='check_minio',
    python_callable=check_new_files_in_minio,
    dag=dag,
)

# task 3: check data in ClickHouse
def assert_clickhouse_has_data():
    client = Client(host=CLICKHOUSE_HOST, port=9000)
    
    try:
        direct = client.execute("SELECT count() FROM s3('http://minio:9050/music-events/data/*.parquet', 'minioadmin', 'minioadmin', 'Parquet')")
        print(f"[check_clickhouse] direct s3 function count: {direct[0][0]}")
    except Exception as e:
        print(f"[check_clickhouse] direct s3 function error: {e}")

    result = client.execute("SELECT count() FROM music_analytics.events")
    count = result[0][0]
    print(f"[check_clickhouse] events table row count: {count}")
    if count == 0:
        raise ValueError("ClickHouse events table is empty — MinIO data not visible!")

check_clickhouse = PythonOperator(
    task_id='check_clickhouse',
    python_callable=assert_clickhouse_has_data,
    dag=dag,
)

# task 4: run dbt
profile_config = ProfileConfig(
    profile_name=DBT_PROFILE_NAME,
    target_name="dev",
    profiles_yml_filepath=f"{DBT_PROJECT_DIR}/profiles.yml"
)

dbt_task_group = DbtTaskGroup(
    group_id="dbt_music_events",
    project_config=ProjectConfig(dbt_project_path=DBT_PROJECT_DIR),
    profile_config=profile_config,
    dag=dag,
)

# task 5: check dbt result
check_dbt = ClickHouseOperator(
    task_id='check_dbt_results',
    clickhouse_conn_id='clickhouse_default',
    sql=[
        # 1. check view staging
        "SELECT count() FROM music_analytics.stg_events",
        "SELECT count() FROM music_analytics.fct_listens",

        # 2. check mart tables
        "SELECT count() FROM music_analytics.mart_top_artists",
        "SELECT count() FROM music_analytics.mart_hourly_trends",
        "SELECT count() FROM music_analytics.mart_location_stats",
        "SELECT count() FROM music_analytics.mart_user_play_counts",

        # 3. spot-check data
        "SELECT artist, play_count FROM music_analytics.mart_top_artists ORDER BY play_count DESC LIMIT 5",
        "SELECT hour_timestamp, total_listens FROM music_analytics.mart_hourly_trends ORDER BY hour_timestamp DESC LIMIT 5",
        "SELECT location, total_plays FROM music_analytics.mart_location_stats ORDER BY total_plays DESC LIMIT 5",

        # 4. spot-check ALS input matrix
        "SELECT user_id, song, play_count FROM music_analytics.mart_user_play_counts ORDER BY play_count DESC LIMIT 5",
    ],
    dag=dag,
)

# task 6: run ALS model for recommendations
# using BashOperator to bypass Airflow's default 'spark_default' yarn connection
from airflow.operators.bash import BashOperator
run_als = BashOperator(
    task_id='run_als',
    bash_command=f"spark-submit --master 'local[*]' --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262,com.clickhouse:clickhouse-jdbc:0.4.6 {ALS_APP_PATH}",
    dag=dag,
)

# task 7: verify recommendations were written
def check_recommendations_in_minio(**context):
    s3 = boto3.client(
        's3',
        endpoint_url=MINIO_ENDPOINT_URL,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )
    # Prefix='recommendations' matches Spark's path s3a://music-events/recommendations
    response = s3.list_objects_v2(Bucket='music-events', Prefix='recommendations')
    all_files = response.get('Contents', [])
    print(f"[check_recommendations] total files in recommendations: {len(all_files)}")
    
    parquet_files = [f for f in all_files if f['Key'].endswith('.parquet')]
    print(f"[check_recommendations] found {len(parquet_files)} parquet files")
    
    if len(parquet_files) == 0:
        raise ValueError("No recommendation parquet files found in MinIO!")

check_recommendations = PythonOperator(
    task_id='check_recommendations',
    python_callable=check_recommendations_in_minio,
    dag=dag,
)

# task dependencies
check_minio >> check_clickhouse >> dbt_task_group >> check_dbt >> run_als >> check_recommendations