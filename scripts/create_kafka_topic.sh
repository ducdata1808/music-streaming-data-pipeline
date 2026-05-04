#!/bin/bash
echo "=================================="
echo "    Create Kafka Topic: music_events"
echo "=================================="

KAFKA_TOPICS="/home/duc1808/kafka/kafka_2.13-3.6.1/bin/kafka-topics.sh"

if [ ! -f "$KAFKA_TOPICS" ]; then
    echo "kafka shell script not found at $KAFKA_TOPICS"
    exit 1
fi

# Wait until Kafka is ready on port 9092
echo "Waiting for Kafka to be ready..."
MAX_RETRIES=15
COUNT=0
until ss -tlnp | grep -q 9092 || [ $COUNT -ge $MAX_RETRIES ]; do
    echo "  Kafka not ready yet, retrying in 2s... ($COUNT/$MAX_RETRIES)"
    sleep 2
    COUNT=$((COUNT + 1))
done

if [ $COUNT -ge $MAX_RETRIES ]; then
    echo "ERROR: Kafka did not start after $((MAX_RETRIES * 2)) seconds. Is run_kafka.py running?"
    exit 1
fi

echo "Kafka is ready! Creating topic..."

$KAFKA_TOPICS --create \
    --topic music_events \
    --bootstrap-server localhost:9092 \
    --partitions 1 \
    --replication-factor 1 \
    --if-not-exists

echo "Done!"
