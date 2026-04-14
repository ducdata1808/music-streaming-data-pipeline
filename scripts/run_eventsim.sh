#!/bin/bash
echo "=================================="
echo " Starting EventSim -> Kafka Pipe"
echo "=================================="

EVENTSIM_DIR="/home/duc1808/eventsim"
if [ ! -d "$EVENTSIM_DIR" ]; then
    EVENTSIM_DIR="/home/duc1808/eventsim_project/eventsim"
fi

KAFKA_PRODUCER="/home/duc1808/kafka/kafka_2.13-3.6.1/bin/kafka-console-producer.sh"

cd "$EVENTSIM_DIR" || { echo "eventSim not found at $EVENTSIM_DIR"; exit 1; }

stdbuf -oL ./bin/eventsim -c "examples/example-config.json" \
    -n 2000 \
    --start-time "2026-04-06T00:00:00" \
    --end-time "2099-01-01T00:00:00" \
    --continuous | stdbuf -i0 -oL $KAFKA_PRODUCER --bootstrap-server localhost:9092 --topic music_events
