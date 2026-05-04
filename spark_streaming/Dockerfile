# =============================================================================
# Dockerfile for Spark Streaming
# Project: Music Events Data Pipeline
# Base: apache/spark:3.5.3-scala2.12-java17-python3-ubuntu
# =============================================================================
FROM apache/spark:3.5.3-scala2.12-java17-python3-ubuntu

# Switch to root for setup
USER root

# Install pip (apache/spark image may not include pip by default)
RUN apt-get update && apt-get install -y python3-pip --no-install-recommends \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app
COPY . /app/spark_streaming

# Install Python dependencies required by run_spark.py
RUN pip3 install --no-cache-dir colorama

# Create entrypoint script
# Note: apache/spark uses /opt/spark/bin/spark-submit (not bitnami's path)
RUN printf '#!/bin/bash\n\
echo "Cleaning up old checkpoints..."\n\
rm -rf /app/checkpoints/*\n\
\n\
echo "Starting Spark Streaming Job..."\n\
/opt/spark/bin/spark-submit \\\n\
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \\\n\
    --conf "spark.driver.host=0.0.0.0" \\\n\
    /app/spark_streaming/run_spark.py\n' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Set the Python environment
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
