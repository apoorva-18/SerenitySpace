/* global use, db */
// MongoDB Playground

// Define the database and collection names
const database = 'mongodbVSCodePlaygroundDB';
const diaryCollection = 'diary_entries';

// Switch to the target database
use(mongodbVSCodePlaygroundDB);

// Create the 'users' collection (only needed if specific options are required; otherwise, collections are created when data is inserted)
db.createCollection(diaryCollection);

// Insert a sample user into the 'users' collection
db[diaryCollection].insertOne({
  "user_id": ObjectId("648f9b6c9f0f5c24d9a78b5d"),
  "date": new Date(),
  "mood": "Happy",
  "thoughts": "Feeling great today!"
});
