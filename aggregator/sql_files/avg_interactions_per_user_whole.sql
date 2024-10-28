SELECT user_id, COUNT(*) AS interaction_count
FROM SOURCE
GROUP BY user_id

-- for_each_batch
SELECT '_id' AS _id, AVG(interaction_count) AS avg_interactions_per_user
FROM AGGREGATED
-- end_for
