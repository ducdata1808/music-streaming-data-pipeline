FROM apache/airflow:2.10.4-python3.12

# Switch to root to install system-level dependencies
USER root

# Install Java (required for SparkSubmitOperator to talk to Spark)
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jdk-headless \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME so Spark/Airflow can locate it
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Switch back to airflow user for pip installs (security best practice)
USER airflow

# Copy only the Python dependency file first (layer caching)
COPY requirements-airflow.txt /requirements-airflow.txt

# Install Airflow providers and project-specific Python packages
# The constraint file pins all transitive deps to versions tested with Airflow 2.10.4
RUN pip install --no-cache-dir \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.4/constraints-3.12.txt" \
    apache-airflow-providers-apache-spark \
    apache-airflow-providers-http \
    apache-airflow-providers-amazon \
    airflow-clickhouse-plugin \
    astronomer-cosmos \
    && pip install --no-cache-dir -r /requirements-airflow.txt

# Copy DAG files into the container
COPY dag.py /opt/airflow/dags/dag.py

# Expose Airflow Webserver port
EXPOSE 8080

# Default command: start the webserver
# (Override in docker-compose.yaml for scheduler / triggerer)
CMD ["airflow", "webserver"]
