#!/bin/bash
echo "=================================="
echo "        Starting MinIO"
echo "=================================="

export MINIO_ROOT_USER=minioadmin
export MINIO_ROOT_PASSWORD=minioadmin

MINIO_DATA="$HOME/MinIO/minio_data"

MINIO_BIN="$HOME/minio"

mkdir -p "$MINIO_DATA"

$MINIO_BIN server "$MINIO_DATA" --address ":9050" --console-address ":9051"
