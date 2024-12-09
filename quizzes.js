/* global use, db */
// MongoDB Playground

// Define the database and collection names
const database = 'mongodbVSCodePlaygroundDB';
const quizCollection = 'quizzes';

// Switch to the target database
use(mongodbVSCodePlaygroundDB);

// Create the 'users' collection (only needed if specific options are required; otherwise, collections are created when data is inserted)
db.createCollection(quizCollection);

// Insert a sample user into the 'users' collection
db[quizCollection].insertMany({
    "_id": "ObjectId",
    "title": "How are you feeling today?",
    "questions": [
      {
        "question": "How often do you feel anxious?",
        "options": ["Rarely", "Sometimes", "Often", "Always"]
      }
    ]
  }
  );
