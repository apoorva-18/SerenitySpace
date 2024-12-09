/* global use, db */
// MongoDB Playground

// Define the database and collection names
const database = 'mongodbVSCodePlaygroundDB';
const challengesCollection = 'challenges';

// Switch to the target database
use(mongodbVSCodePlaygroundDB);

// Create the 'users' collection (only needed if specific options are required; otherwise, collections are created when data is inserted)
db.createCollection(challengesCollection);

// Insert a sample user into the 'users' collection
db[challengesCollection].insertMany({
    "_id": "ObjectId",
    "title": "5 Minutes of Mindfulness",
    "description": "Spend 5 minutes meditating daily.",
    "start_date": "2024-11-25",
    "end_date": "2024-12-01"
  }
  
  );
