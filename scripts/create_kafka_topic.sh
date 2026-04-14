#!/bin/bash
echo "=================================="
echo "    Create Kafka Topic: music_events"
echo "=================================="

KAFKA_TOPICS="/home/duc1808/kafka/kafka_2.13-3.6.1/bin/kafka-topics.sh"

if [ ! -f "$KAFKA_TOPICS" ]; then
    echo "kafka shell script not found at $KAFKA_TOPICS"
    exit 1
fi

$KAFKA_TOPICS --create \
    --topic music_events \
    --bootstrap-server localhost:9092 \
    --partitions 1 \
    --replication-factor 1

echo "Done!"
