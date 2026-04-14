#!/bin/bash
echo "=================================="
echo "      Starting Airflow"
echo "=================================="

export AIRFLOW_HOME="$HOME/eventsim_project"
export AIRFLOW__CORE__DAGS_FOLDER="$HOME/eventsim_project/airflow"

airflow standalone
