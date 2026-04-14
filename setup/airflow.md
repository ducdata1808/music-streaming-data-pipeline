# Airflow Setup Guide

Apache Airflow is used in this project to orchestrate the execution of tasks, such as tracking data streams and running DBT transformations.

## 1. Prerequisites and Installation

Airflow is a Python package and should be installed within our project's **Virtual Environment** rather than globally on your system.

```bash
# 1. Ensure you are in the project folder
cd ~/eventsim_project

# 2. Activate your virtual environment
source venv/bin/activate

# 3. Install Airflow and providers (from requirements.txt)
pip install -r requirements.txt
```

## 2. Configuration (`AIRFLOW_HOME`)

To keep our project self-contained, we configure Airflow to use the project folder as its home directory. This is handled automatically by our helper scripts, but if you run Airflow manually, always export:

```bash
export AIRFLOW_HOME="$HOME/eventsim_project"
export AIRFLOW__CORE__DAGS_FOLDER="$HOME/eventsim_project/airflow"
```

## 3. Creating Required Connections
Our Airflow DAG (`music_events_pipeline`) requires access to MinIO, ClickHouse, and Spark. You must declare these connections in Airflow.
You can do this via the Web UI (Admin -> Connections) or by running these commands directly in your terminal:

```bash
# Don't forget to export your Airflow Home before running this!
export AIRFLOW_HOME="$HOME/eventsim_project"

# MinIO connection
airflow connections add 'minio_default' \
    --conn-type 'aws' \
    --conn-extra '{"endpoint_url": "http://localhost:9050", "aws_access_key_id": "minioadmin", "aws_secret_access_key": "minioadmin"}'

# ClickHouse connection (Native Protocol Port: 9000)
airflow connections add 'clickhouse_default' \
    --conn-type 'clickhouse' \
    --conn-host 'localhost' \
    --conn-port 9000 \
    --conn-login 'default' \
    --conn-password '' \
    --conn-schema 'music_analytics'

# Spark connection
airflow connections add 'spark_default' \
    --conn-type 'spark' \
    --conn-host 'local' \
    --conn-extra '{"master": "local[*]"}'
```

*(Note: Verify connections by running `airflow connections list` in the terminal)*

## 4. Starting Airflow (Web Server & Scheduler)

We use a helper script that points Airflow to our local DAGs folder inside the project and spins up the standalone module:

```bash
~/eventsim_project/scripts/run_airflow.sh
```

- **Login info:** Check the terminal output for the **admin password**. 
- You can log into the UI at `http://localhost:8080/` using Username: `admin`.

## 5. Triggering the Data Pipeline

Once Airflow scans `~/eventsim_project/airflow/` and imports defined DAGs, you can manually trigger the pipeline from the Web UI or via terminal using:

```bash
# Remember to activate your venv first
source ~/eventsim_project/scripts/activate_venv.sh
~/eventsim_project/scripts/trigger_airflow.sh
```

You can view running tasks by accessing the Web UI or executing:
```bash
airflow dags list-runs -d music_events_pipeline
```

View dag moore details:
```bash
airflow tasks states-for-dag-run music_events_pipeline <run_id>
```