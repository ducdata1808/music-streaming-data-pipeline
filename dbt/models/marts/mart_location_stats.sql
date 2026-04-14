-- create table for location stats
SELECT
    location,
    count(*) AS total_plays,
    count(DISTINCT user_id) AS unique_users,
    splitByChar(',', location)[1] AS city
FROM {{ ref('fct_listens') }}
GROUP BY location
ORDER BY total_plays DESC