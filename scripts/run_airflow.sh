#!/bin/bash
echo "=================================="
echo "      Starting Airflow"
echo "=================================="

# Activate virtual environment
VENV_PATH="$HOME/eventsim_project/venv/bin/activate"
if [ ! -f "$VENV_PATH" ]; then
    echo "ERROR: Virtual environment not found at $VENV_PATH"
    exit 1
fi
source "$VENV_PATH"

# Airflow config
export AIRFLOW_HOME="$HOME/eventsim_project"
export AIRFLOW__CORE__DAGS_FOLDER="$HOME/eventsim_project/airflow"

# Local paths for DAG tasks (overrides Docker defaults in dag.py)
export SPARK_APP_PATH="$HOME/eventsim_project/spark_streaming/run_spark.py"
export ALS_APP_PATH="$HOME/eventsim_project/spark_streaming/run_als.py"
export DBT_PROJECT_DIR="$HOME/eventsim_project/dbt"
export MINIO_ENDPOINT="http://localhost:9050"
export CLICKHOUSE_HOST="localhost"

airflow standalone
