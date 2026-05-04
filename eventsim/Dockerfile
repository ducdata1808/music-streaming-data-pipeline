# =============================================================================
# Dockerfile for EventSim
# Project: Music Events Data Pipeline
# Base: eclipse-temurin:8-jdk-jammy
# =============================================================================
FROM eclipse-temurin:8-jdk-jammy AS builder

# Install sbt
RUN apt-get update && apt-get install -y curl gnupg git && \
    echo "deb https://repo.scala-sbt.org/scalasbt/debian all main" | tee /etc/apt/sources.list.d/sbt.list && \
    echo "deb https://repo.scala-sbt.org/scalasbt/debian /" | tee -a /etc/apt/sources.list.d/sbt.list && \
    curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | apt-key add && \
    apt-get update && apt-get install -y sbt

# Clone EventSim source code from GitHub
RUN git clone https://github.com/Interana/eventsim.git /app

WORKDIR /app

RUN sbt assembly

# Runtime stage
FROM eclipse-temurin:8-jre-jammy
RUN apt-get update && apt-get install -y curl procps && rm -rf /var/lib/apt/lists/*

ENV KAFKA_VERSION=3.6.1
ENV SCALA_VERSION=2.13
# Download and install Kafka
RUN curl -O https://archive.apache.org/dist/kafka/${KAFKA_VERSION}/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz && \
    tar -xzf kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz && \
    mv kafka_${SCALA_VERSION}-${KAFKA_VERSION} /opt/kafka && \
    rm kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz

WORKDIR /app

COPY --from=builder /app/target/scala-2.12/eventsim-assembly-1.0.jar ./eventsim.jar
# examples/ directory is taken from the cloned repo in builder stage
COPY --from=builder /app/examples ./examples

ENV KAFKA_BOOTSTRAP_SERVER="kafka:9092"
ENV KAFKA_TOPIC="music_events"
ENV N_RECORDS=2000

# Copy and setup run script
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

ENTRYPOINT ["/app/run.sh"]
