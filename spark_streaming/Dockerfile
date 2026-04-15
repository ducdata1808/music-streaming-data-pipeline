FROM bitnami/spark:3.5.8

USER root
RUN pip install --no-cache-dir pyspark==3.5.8

WORKDIR /app
COPY . /app/spark_streaming

RUN echo '#!/bin/bash\n\
echo "Cleaning up old checkpoints..."\n\
rm -rf /app/checkpoints/*\n\
\n\
echo "Starting Spark Streaming Job..."\n\
spark-submit \\\n\
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.8,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \\\n\
    --conf "spark.driver.host=127.0.0.1" \\\n\
    /app/spark_streaming/run_spark.py' > /opt/bitnami/scripts/spark/entrypoint.sh && \
    chmod +x /opt/bitnami/scripts/spark/entrypoint.sh

ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

ENTRYPOINT [ "/opt/bitnami/scripts/spark/entrypoint.sh" ]
