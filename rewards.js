/* global use, db */
// MongoDB Playground

// Define the database and collection names
const database = 'mongodbVSCodePlaygroundDB';
const rewards_Collection = 'rewards';

// Switch to the target database
use(database);

// Create the 'users' collection (only needed if specific options are required; otherwise, collections are created when data is inserted)
db.createCollection(rewards_Collection);

// Insert a sample user into the 'users' collection
db[rewards_Collection].insertOne({
    "user_id": "ObjectId",
    "badges": ["Mindfulness Master", "Streak Keeper"],
    "points": 1200
      
});
