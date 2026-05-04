#!/bin/bash
echo "Starting EventSim -> Kafka Pipe ($KAFKA_BOOTSTRAP_SERVER)"
java -jar eventsim.jar -c "examples/example-config.json" \
    -n $N_RECORDS \
    --start-time "$(date -u +"%Y-%m-%dT%H:%M:%S")" \
    --end-time "$(date -u -d '+1 day' +"%Y-%m-%dT%H:%M:%S")" \
    --continuous | grep --line-buffered '^{' | /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $KAFKA_BOOTSTRAP_SERVER --topic $KAFKA_TOPIC
