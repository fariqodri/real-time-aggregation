SELECT item_id, COUNT(*) AS interaction_count
FROM SOURCE
GROUP BY item_id

-- for_each_batch
SELECT '_id' AS _id, AVG(interaction_count) AS avg_interactions_per_item
FROM AGGREGATED
-- end_for
