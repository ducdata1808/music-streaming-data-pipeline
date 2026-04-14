#!/bin/bash
echo "=================================="
echo "    Starting Spark Streaming"
echo "=================================="

export PYSPARK_PYTHON=$(which python3)
export PYSPARK_DRIVER_PYTHON=$(which python3)

# move to root directory
cd /home/duc1808/eventsim_project || { echo "eventsim_project not found at /home/duc1808/eventsim_project!"; exit 1; }

spark-submit \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.8,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
    --conf "spark.driver.host=127.0.0.1" \
    spark_streaming/run_spark.py
