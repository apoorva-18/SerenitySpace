/* global use, db */
// MongoDB Playground

// Define the database and collection names
const database = 'mongodbVSCodePlaygroundDB';
const usersCollection = 'users';

// Switch to the target database
use(mongodbVSCodePlaygroundDB);

// Create the 'users' collection (only needed if specific options are required; otherwise, collections are created when data is inserted)
db.createCollection(usersCollection);

// Insert a sample user into the 'users' collection
db[usersCollection].insertOne({
  "_id": ObjectId("648f9b6c9f0f5c24d9a78b5d"),
  "username": "JohnDoe",
  "email": "john.doe@example.com",
  "password": "your_secure_password_here" 
});
