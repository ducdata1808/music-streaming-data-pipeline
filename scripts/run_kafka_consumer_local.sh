#!/bin/bash
echo "=================================="
echo " Kafka Consumer (LOCAL - port 9092)"
echo "=================================="

KAFKA_CONSUMER="/home/duc1808/kafka/kafka_2.13-3.6.1/bin/kafka-console-consumer.sh"

if [ ! -f "$KAFKA_CONSUMER" ]; then
    echo "ERROR: kafka-console-consumer.sh not found at $KAFKA_CONSUMER"
    exit 1
fi

echo "Listening to topic 'music_events' on LOCAL Kafka (localhost:9092)..."
echo "Press Ctrl+C to stop."
echo "----------------------------------"

$KAFKA_CONSUMER \
    --bootstrap-server localhost:9092 \
    --topic music_events \
    --from-beginning
