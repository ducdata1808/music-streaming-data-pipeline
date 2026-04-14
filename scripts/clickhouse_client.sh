#!/bin/bash
echo "=================================="
echo "    Open ClickHouse Client CLI"
echo "=================================="

CLICKHOUSE_BIN="/home/duc1808/clickhouse/clickhouse"

if [ ! -f "$CLICKHOUSE_BIN" ]; then
    echo "clickhouse not found at $CLICKHOUSE_BIN"
    exit 1
fi

$CLICKHOUSE_BIN client
