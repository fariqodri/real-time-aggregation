WITH aggregation AS (
    SELECT
        WINDOW(timestamp, '5 minutes') AS window,
        COUNT(*) AS interaction_count,
        approx_count_distinct(item_id) AS num_item,
        COUNT(*) / approx_count_distinct(item_id) AS avg_interactions_per_item
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
