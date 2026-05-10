-- mart_user_play_counts: aggregate play counts per user per song
-- used as input matrix for ALS collaborative filtering model
-- rows = users, columns = songs, values = number of times played

SELECT
    user_id,
    song,
    artist,
    count(*) AS play_count
FROM {{ ref('fct_listens') }}
GROUP BY user_id, song, artist
ORDER BY play_count DESC
