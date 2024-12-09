/* global use, db */
// MongoDB Playground

// Define the database and collection names
const database = 'mongodbVSCodePlaygroundDB';
const forum_posts_Collection = 'forum_posts';

// Switch to the target database
use(mongodbVSCodePlaygroundDB);

// Create the 'users' collection (only needed if specific options are required; otherwise, collections are created when data is inserted)
db.createCollection(forum_posts_Collection);

// Insert a sample user into the 'users' collection
db[forum_posts_Collection].insertOne({
        "_id": "ObjectId",
        "user_id": "User's ObjectId",
        "username": "JohnDoe",
        "title": "Post Title",
        "content": "Post Content",
        "created_at": "2024-11-25T10:00:00Z",
        "comments": [
          {
            "_id": "ObjectId",
            "username": "JaneDoe",
            "content": "This is a comment",
            "user_id": "User's ObjectId",
            "created_at": "2024-11-25T11:00:00Z"
          }
        ]
    });
      

