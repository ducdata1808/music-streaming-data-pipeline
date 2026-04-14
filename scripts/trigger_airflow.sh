#!/bin/bash
echo "=================================="
echo "  Trigger Airflow DAG manually"
echo "=================================="

DAG_ID="music_events_pipeline"

echo "Triggering $DAG_ID..."
airflow dags trigger $DAG_ID

echo "Done! Open UI http://[IP_ADDRESS] to view the process."
