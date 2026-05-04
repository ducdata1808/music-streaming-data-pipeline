#!/bin/bash
echo "=================================="
echo "  Trigger Airflow DAG manually"
echo "=================================="

# Activate virtual environment (required for airflow CLI to be found)
VENV_PATH="$HOME/eventsim_project/venv/bin/activate"
if [ ! -f "$VENV_PATH" ]; then
    echo "ERROR: Virtual environment not found at $VENV_PATH"
    echo "Please run: python3 -m venv ~/eventsim_project/venv && pip install apache-airflow"
    exit 1
fi
source "$VENV_PATH"

export AIRFLOW_HOME="$HOME/eventsim_project"
export AIRFLOW__CORE__DAGS_FOLDER="$HOME/eventsim_project/airflow"

DAG_ID="music_events_pipeline"

echo "Triggering $DAG_ID..."
airflow dags trigger $DAG_ID

echo "Done! Open UI http://localhost:8080 to view the process."
