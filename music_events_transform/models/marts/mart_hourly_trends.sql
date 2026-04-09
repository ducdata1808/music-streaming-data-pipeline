-- create table for hourly trends

SELECT
    toStartOfHour(event_time) AS hour_timestamp,
    count(*) AS total_listens,
    count(DISTINCT user_id) AS unique_listeners
FROM {{ ref('fct_listens') }}
GROUP BY hour_timestamp
ORDER BY hour_timestamp ASC