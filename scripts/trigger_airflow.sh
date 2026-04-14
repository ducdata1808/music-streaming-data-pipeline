#!/bin/bash
echo "=================================="
echo "  Trigger Airflow DAG manually"
echo "=================================="

export AIRFLOW_HOME="$HOME/eventsim_project"
export AIRFLOW__CORE__DAGS_FOLDER="$HOME/eventsim_project/airflow"

DAG_ID="music_events_pipeline"

echo "Triggering $DAG_ID..."
airflow dags trigger $DAG_ID

echo "Done! Open UI http://[IP_ADDRESS] to view the process."
