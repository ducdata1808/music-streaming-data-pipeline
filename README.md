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

![image not found](images/version1.png)
---

## 📁 Project Directory Structure

```text
~ (Home Directory)
├── eventsim_project/        # Main project repository
│   ├── airflow/             # Airflow DAGs and configurations
│   ├── dbt/                 # DBT models and macros for transformations
│   ├── kafka/               # Custom scripts for Kafka automation
│   ├── scripts/             # Shell scripts to manage services (start, stop, etc.)
│   ├── setup/               # Setup guides for each service (.md files)
│   ├── spark_streaming/     # PySpark structured streaming scripts
│   └── README.md            # Project documentation
├── eventsim/                # EventSim (Data Generator) repository clone
├── kafka_2.13-3.6.1/        # Kafka installation binaries & properties
├── minio                    # MinIO server executable binary
└── MinIO/
    └── minio_data/          # MinIO Data Lake storage (Parquet files)
```
*Note: ClickHouse is installed system-wide (Global installation), which usually places executables in `/usr/bin/clickhouse` and data in `/var/lib/clickhouse/`.*

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
To spin up the entire pipeline, make sure you have granted execution p instances in the following order:

1. **Setup Virtual Environment** (If you haven't already):
   ```bash
   python3 -m venv ~/eventsim_project/venv
   source ~/eventsim_project/venv/bin/activate
   pip install -r ~/eventsim_project/requirements.txt
   ```

2. **Start Kafka & Zookeeper** (Depends on your local installation):
   ```bash
   python3 ~/eventsim_project/kafka/run_kafka.py
   ```
3. **Create the Kafka Topic** (Only needed the first time):
   Grant execution permission to the script:
   ```bash
   chmod +x ~/eventsim_project/scripts/*.sh
   ```
   Run the script:
   ```bash
   ~/eventsim_project/scripts/create_kafka_topic.sh
   ```
4. **Start the Data Stream**:
   ```bash
   ~/eventsim_project/scripts/run_eventsim.sh
   ```
   Turn on Kafka consumer to check the data stream:
   ```bash
   ~/eventsim_project/scripts/run_kafka_consumer.sh
   ```
5. **Start the Data Lake**:
   ```bash
   ~/eventsim_project/scripts/run_minio.sh
   ```
6. **Start Spark Processor**:
   ```bash
   ~/eventsim_project/scripts/run_spark.sh
   ```
   Turn on browser, go to http://localhost:9051/login, user: minioadmin, password: minioadmin
   ![image not found](images/minio_web.png)
7. **Start Analytics Database**:
   ```bash
   ~/eventsim_project/scripts/run_clickhouse.sh
   # And to interact with it:
   ~/eventsim_project/scripts/clickhouse_client.sh
   ```
8. **Orchestrate Transformations**:
   ```bash
   source ~/eventsim_project/scripts/activate_venv.sh
   ~/eventsim_project/scripts/run_airflow.sh
   # And to run the pipeline visually/manually:
   ~/eventsim_project/scripts/trigger_airflow.sh
   ```
9. **Run app to check the result**:
   ```bash
   ~/eventsim_project/scripts/run_app.sh
   ```
   ![image not found](images/top_artists.png)