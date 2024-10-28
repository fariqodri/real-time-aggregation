// mongo-init.js

// Connect to the database
const db = connect('mongodb://localhost:27017/avrioc-test');

// Create collections
db.createCollection('interactions_per_item_5m');
db.createCollection('interactions_per_user_5m');

// Create indexes
db.interactions_per_item_5m.createIndex({ day: -1 });
db.interactions_per_user_5m.createIndex({ day: -1 });

print("Database and collections created successfully!");
