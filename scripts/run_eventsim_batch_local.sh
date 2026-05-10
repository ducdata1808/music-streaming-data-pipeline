#!/bin/bash
echo "=================================="
echo " Starting EventSim -> Kafka (BATCH MODE)"
echo "=================================="
echo "This will generate ~100,000 events as fast as possible and then stop."

EVENTSIM_DIR="/home/duc1808/eventsim"
if [ ! -d "$EVENTSIM_DIR" ]; then
    EVENTSIM_DIR="/home/duc1808/eventsim_project/eventsim"
fi

KAFKA_PRODUCER="/home/duc1808/kafka/kafka_2.13-3.6.1/bin/kafka-console-producer.sh"

if [ ! -f "$KAFKA_PRODUCER" ]; then
    echo "ERROR: kafka-console-producer.sh not found at $KAFKA_PRODUCER"
    exit 1
fi

cd "$EVENTSIM_DIR" || { echo "ERROR: EventSim not found at $EVENTSIM_DIR"; exit 1; }

# NO --continuous flag here!
# Time window: 3 days ago -> Now (Simulates 3 days of traffic for 2000 users = ~100k+ events)
# EventSim will use 100% CPU to generate this instantly, then exit.

stdbuf -oL ./bin/eventsim -c "examples/example-config.json" \
    -n 2000 \
    --start-time "$(date -u -d '3 days ago' +"%Y-%m-%dT%H:%M:%S")" \
    --end-time "$(date -u +"%Y-%m-%dT%H:%M:%S")" \
    | grep --line-buffered '^{' | stdbuf -i0 -oL "$KAFKA_PRODUCER" --bootstrap-server localhost:9092 --topic music_events

echo "=================================="
echo " Batch generation completed!"
echo "=================================="
