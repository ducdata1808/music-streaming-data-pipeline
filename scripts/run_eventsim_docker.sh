#!/bin/bash
echo "=================================="
echo " Starting EventSim -> Kafka (DOCKER)"
echo "=================================="

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

# connect to kafka topic music_events (docker)
stdbuf -oL ./bin/eventsim -c "examples/example-config.json" \
    -n 2000 \
    --start-time "$(date -u +"%Y-%m-%dT%H:%M:%S")" \
    --end-time "2099-12-31T23:59:59" \
    --continuous | grep --line-buffered '^{' | stdbuf -i0 -oL "$KAFKA_PRODUCER" --bootstrap-server localhost:29092 --topic music_events
