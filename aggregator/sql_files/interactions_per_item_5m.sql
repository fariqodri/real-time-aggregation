WITH aggregation AS (
    SELECT
        item_id,
        interaction_type AS interaction_type,
        WINDOW(timestamp, '5 minutes') AS window,
        COUNT(*) AS interaction_count
    FROM 
        SOURCE
    GROUP BY
        item_id,
        interaction_type,
        window
)
SELECT
    CONCAT_WS('#', item_id, interaction_type, window.start, window.end) AS _id,
    *
FROM 
    aggregation