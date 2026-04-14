# Kafka Setup Guide

Apache Kafka handles the real-time event streaming portion of the project.

## 1. Installation

Download and extract Kafka 3.6.1 (with Scala 2.13 support):
```bash
cd ~
wget https://archive.apache.org/dist/kafka/3.6.1/kafka_2.13-3.6.1.tgz
tar -xzf kafka_2.13-3.6.1.tgz
cd kafka_2.13-3.6.1
```

## 2. Starting Kafka & Zookeeper

> [!TIP]
> **Use the Python Automation Script:**
> Rather than opening separate terminals, you can launch everything in the background:
> ```bash
> cd ~/kafka
> python3 run_kafka.py
> ```
> Press `Ctrl+C` cleanly tears down both systems.

### Manual way
If you prefer the manual way, you need two terminals:
- **Terminal 1** (Zookeeper): `bin/zookeeper-server-start.sh config/zookeeper.properties`
- **Terminal 2** (Kafka Broker): `bin/kafka-server-start.sh config/server.properties`

## 3. Managing Topics

### Create the Topic
We need a topic named `music_events`. Use our helper script:
```bash
cd ~/eventsim_project/scripts
./create_kafka_topic.sh
```

### Checking Data Flow
If you want to view incoming data in real-time, launch a console consumer:
```bash
~/kafka/kafka_2.13-3.6.1/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic music_events \
  --from-beginning
```

> [!WARNING]
> Since we stream continuous simulated data, configuring volume retention properly is essential so your hard drive doesn't run out of memory.
