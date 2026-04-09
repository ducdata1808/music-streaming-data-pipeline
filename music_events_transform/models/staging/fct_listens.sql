-- create view for watching detail log
-- fix: ClickHouse is case-sensitive, use MD5 not md5, fromUnixTimestamp not from_unixtime
SELECT
    hex(MD5(concat(userId, ts, toString(sessionId)))) AS event_id,
    fromUnixTimestamp(intDiv(toInt64(ts), 1000)) AS event_time,
    userId AS user_id,
    sessionId AS session_id,
    artist,
    song,
    length,
    page,
    location
FROM {{ source('music_analytics', 'events') }}
WHERE userId IS NOT NULL
  AND page = 'NextSong'