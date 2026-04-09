-- top artists by listen count
-- note: 'length' column from source is duration in seconds

SELECT
    artist,
    count(*) AS play_count,
    count(DISTINCT user_id) AS unique_listeners,
    round(sum(length) / 60, 2) AS total_minutes_played
FROM {{ ref('fct_listens') }}
GROUP BY artist
ORDER BY play_count DESC