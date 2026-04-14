# Music Events Data Pipeline

A comprehensive, real-time data engineering pipeline simulating a music streaming platform's analytics. 

## 🗺️ Architecture Overview
This project simulates user listening behavior and pipes the data through an end-to-end modern data stack:
1. **EventSim:** Generates simulated JSON user interactions (plays, skips, signups).
2. **Kafka:** Captures streaming events as the primary message broker.
3. **PySpark (Structured Streaming):** Consumes Kafka topics, parses the data, and writes to Data Lake in Parquet format.
4. **MinIO:** Acts as the S3-compatible Object Storage (Data Lake).
5. **ClickHouse:** High-performance OLAP database connecting directly to our MinIO S3 bucket.
6. **DBT (Data Build Tool):** Applies transformations (ELT) inside ClickHouse to build staging schemas and data marts.
7. **Apache Airflow:** Orchestrates the manual Spark jobs, DBT models, and manages pipeline dependencies.

---

## 🛠️ Detailed Setup Guides
If you are deploying this for the first time, or need to rebuild a component, please refer to the detailed, step-by-step installation guides in the `setup/` directory:

- [Setup EventSim](setup/eventsim.md)
- [Setup Kafka](setup/kafka.md)
- [Setup MinIO](setup/minio.md)
- [Setup ClickHouse](setup/clickhouse.md)
- [Setup Spark](setup/spark.md)
- [Setup DBT](setup/dbt.md)

---

## 🚀 Quick Start
To spin up the entire pipeline, make sure you have granted execution permissions to our helper scripts:
```bash
cd ~/eventsim_project/scripts
chmod +x *.sh
```

**Boot Order:** Open separate terminals or use background processes to start the instances in the following order:

1. **Start Kafka & Zookeeper** (Depends on your local installation):
   ```bash
   cd ~/kafka
   python3 run_kafka.py
   ```
2. **Create the Kafka Topic** (Only needed the first time):
   ```bash
   ./scripts/create_kafka_topic.sh
   ```
3. **Start the Data Stream**:
   ```bash
   ./scripts/run_eventsim.sh
   ```
4. **Start the Data Lake**:
   ```bash
   ./scripts/run_minio.sh
   ```
5. **Start Spark Processor**:
   ```bash
   ./scripts/run_spark.sh
   ```
6. **Start Analytics Database**:
   ```bash
   ./scripts/run_clickhouse.sh
   # And to interact with it:
   ./scripts/clickhouse_client.sh
   ```
7. **Orchestrate Transformations**:
   ```bash
   ./scripts/run_airflow.sh
   # And to run the pipeline visually/manually:
   ./scripts/trigger_airflow.sh
   ```
