-- create view for stg_events
-- convert ts to datetime and registration to datetime
-- filter out rows where userId is null or page is not 'NextSong'
-- select only the columns needed for analysis
SELECT
    parseDateTimeBestEffort(ts)         AS event_time,
    parseDateTimeBestEffort(registration) AS registered_at,
    userId,
    sessionId,
    page,
    auth,
    level,
    artist,
    song,
    length,
    firstName,
    lastName,
    gender,
    location,
    userAgent
FROM {{ source('music_analytics', 'events') }}
WHERE userId IS NOT NULL
  AND page = 'NextSong'
