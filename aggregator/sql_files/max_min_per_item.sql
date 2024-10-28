SELECT
    item_id,
    interaction_type,
    COUNT(1) AS interaction_count
FROM
    SOURCE
GROUP BY
    item_id,
    interaction_type;

-- for_each_batch
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY item_id ORDER BY interaction_count DESC) AS rn_most,
        ROW_NUMBER() OVER (PARTITION BY item_id ORDER BY interaction_count ASC) AS rn_least
    FROM
        AGGREGATED
)
SELECT
    item_id AS _id,
    MAX(CASE WHEN rn_most = 1 THEN interaction_type END) AS most_frequent_interaction,
    MAX(CASE WHEN rn_most = 1 THEN interaction_count END) AS most_frequent_count,
    MIN(CASE WHEN rn_least = 1 THEN interaction_type END) AS least_frequent_interaction,
    MIN(CASE WHEN rn_least = 1 THEN interaction_count END) AS least_frequent_count
FROM
    ranked
GROUP BY
    _id;
-- end_for