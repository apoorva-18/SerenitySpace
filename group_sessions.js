/* global use, db */
// MongoDB Playground

// Define the database and collection names
const database = 'mongodbVSCodePlaygroundDB';
const groupSessionCollection = 'group_sessions';

// Switch to the target database
use(database);

// Create the 'users' collection (only needed if specific options are required; otherwise, collections are created when data is inserted)
db.createCollection(groupSessionCollection);

// Insert a sample user into the 'users' collection
db[groupSessionCollection].insertOne({
    "_id": "ObjectId",
    "title": "Stress Management Session",
    "description": "Learn stress management techniques in this interactive session.",
    "time": "2024-11-25T15:00:00Z",
    "max_participants": 20,
    "registered_users": [
        {
            "user_id": "ObjectId",
            "username": "JohnDoe"
        }
    ],
    "created_at": "2024-11-24T10:00:00Z"
}
);
