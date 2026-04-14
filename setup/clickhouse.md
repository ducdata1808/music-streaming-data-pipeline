# ClickHouse Setup Guide

ClickHouse acts as our high-performance analytical database, grabbing files from MinIO via S3 schema.

## 1. Installation

Install ClickHouse server:
```bash
curl https://clickhouse.com/ | sh
sudo ./clickhouse install
```

## 2. Starting Services

Start the server using the helper script:
```bash
cd ~/eventsim_project/scripts
./run_clickhouse.sh
```

Open the client CLI interface:
```bash
cd ~/eventsim_project/scripts
./clickhouse_client.sh
```

## 3. Database & Tables Configuration

Inside the clickhouse client, run the following to setup the `music_analytics` database and the underlying S3 engine table.

```sql
CREATE DATABASE IF NOT EXISTS music_analytics;
USE music_analytics;

DROP TABLE IF EXISTS events;

CREATE TABLE events
(
    ts String,               
    userId String,
    sessionId UInt32,
    page String,
    auth String,
    method String,
    status UInt16,
    level String,
    itemInSession UInt32,
    location String,
    userAgent String,
    lastName String,
    firstName String,
    registration String,     
    gender String,
    artist String,
    song String,
    length Float32
)
ENGINE = S3('http://127.0.0.1:9050/music-events/data/*.parquet', 'minioadmin', 'minioadmin', 'Parquet');
```

> [!CAUTION]
> **Schema Notes:** Spark writes the `ts` column as `INT96`. This poses a challenge where ClickHouse expects a `DateTime`. Make sure your spark script casts `ts` to `String` so DBT handles the string to DateTime cast downstream to prevent schema issues.

To verify data flow:
```sql
SELECT count() FROM events;
SELECT ts, artist, song, firstName FROM events LIMIT 5;
```
