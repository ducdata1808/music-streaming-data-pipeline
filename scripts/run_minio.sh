#!/bin/bash
echo "=================================="
echo "        Starting MinIO"
echo "=================================="

export MINIO_ROOT_USER=minioadmin
export MINIO_ROOT_PASSWORD=minioadmin

MINIO_DATA="/home/duc1808/MinIO/minio_data"

MINIO_BIN="/home/duc1808/minio"
if [ ! -f "$MINIO_BIN" ]; then
    MINIO_BIN="/home/duc1808/eventsim_project/minio"
fi

mkdir -p "$MINIO_DATA"

$MINIO_BIN server "$MINIO_DATA" --address ":9050" --console-address ":9051"
