WITH aggregation AS (
    SELECT
        WINDOW(timestamp, '5 minutes') AS window,
        COUNT(*) AS interaction_count,
        approx_count_distinct(user_id) AS num_users,
        COUNT(*) / approx_count_distinct(user_id) AS avg_interactions_per_user
    FROM
        SOURCE
    GROUP BY
        window
)
SELECT
    CONCAT_WS('#', window.start, window.end) AS _id,
    *
FROM
    aggregation
