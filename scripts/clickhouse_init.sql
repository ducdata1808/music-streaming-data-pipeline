CREATE DATABASE IF NOT EXISTS music_analytics;
USE music_analytics;

DROP TABLE IF EXISTS events;
CREATE TABLE IF NOT EXISTS events
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
ENGINE = S3('http://minio:9050/music-events/data/*.parquet', 'minioadmin', 'minioadmin', 'Parquet');
