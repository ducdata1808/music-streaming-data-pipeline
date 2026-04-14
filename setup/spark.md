# Apache Spark Setup Guide

We use PySpark Structured Streaming to consume data from Kafka, process it, and write it in Parquet format to MinIO.

## 1. Installation

Download Spark and set up paths:
```bash
cd ~
wget https://archive.apache.org/dist/spark/spark-3.5.8/spark-3.5.8-bin-hadoop3.tgz
tar -xzf spark-3.5.8-bin-hadoop3.tgz
```

Add Spark to your `.bashrc` file:
```bash
nano ~/.bashrc
# Add these lines:
export SPARK_HOME=/home/duc1808/spark-3.5.8-bin-hadoop3
export PATH=$PATH:$SPARK_HOME/bin
```
Reload config:
```bash
source ~/.bashrc
spark-submit --version
```

## 2. Running Spark Streaming

### Prepare the Workspace
Be sure you define which Python Spark should use (e.g. from your virtual environment):
```bash
export PYSPARK_PYTHON=$(which python3)
export PYSPARK_DRIVER_PYTHON=$(which python3)
```

> [!TIP]
> If you have errors with checkpoints not syncing to MinIO correctly, you can clear the Checkpoint folder:
> `rm -rf ~/eventsim_project/checkpoints/*`

### The Automated Script
Use the provided shell wrapper to launch Spark. This script automatically handles dependency packages (`hadoop-aws`, `spark-sql-kafka`, `aws-java-sdk`) without remembering them.

```bash
cd ~/eventsim_project/scripts
./run_spark.sh
```

This will run `run_spark.py` which pulls from `music_events` and writes parquet files into the `music_events` bucket on MinIO.
