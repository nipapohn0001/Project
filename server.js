const express = require('express');
const bodyParser = require('body-parser');
const { MongoClient } = require('mongodb');
const app = express();
const PORT = process.env.PORT || 3000;
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/faceRecognition';

app.use(bodyParser.json());

let db;
let studentsCollection;

async function connectToDatabase() {
  try {
    const client = await MongoClient.connect(MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log('Connected to Database');
    db = client.db();
    studentsCollection = db.collection('students');

    // Graceful shutdown
    process.on('SIGINT', async () => {
      try {
        await client.close();
        console.log('MongoDB connection closed.');
        process.exit(0);
      } catch (err) {
        console.error('Error closing MongoDB connection:', err);
        process.exit(1);
      }
    });

  } catch (err) {
    console.error('Failed to connect to MongoDB:', err);
    process.exit(1);
  }
}

// ฟังก์ชันคำนวณ Euclidean Distance
function euclideanDistance(desc1, desc2) {
  return Math.sqrt(
    desc1.reduce((sum, val, i) => sum + Math.pow(val - desc2[i], 2), 0)
  );
}

// API สำหรับตรวจสอบใบหน้า
app.post('/recognize', async (req, res) => {
  const { descriptor } = req.body;

  try {
    const students = await studentsCollection.find().toArray();
    let bestMatch = null;
    let minDistance = 0.6;

    students.forEach(student => {
      const distance = euclideanDistance(descriptor, student.faceDescriptor);
      if (distance < minDistance) {
        bestMatch = student;
        minDistance = distance;
      }
    });

    if (bestMatch) {
      res.status(200).json({
        id: bestMatch.studentId,
        name: bestMatch.name,
        department: bestMatch.department
      });
    } else {
      res.status(404).json({ message: 'No match found' });
    }
  } catch (error) {
    console.error('Error during face recognition:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

// API สำหรับเพิ่มนักเรียน
app.post('/addStudent', async (req, res) => {
  const { studentId, name, department, faceDescriptor, image } = req.body;

  try {
    const result = await studentsCollection.insertOne({
      studentId,
      name,
      department,
      faceDescriptor,
      image
    });
    res.status(201).json({ message: 'Student added successfully', id: result.insertedId });
  } catch (error) {
    console.error('Error adding student:', error);
    res.status(500).json({ message: 'Failed to add student' });
  }
});

// เริ่มต้นแอพพลิเคชัน
async function startApp() {
  await connectToDatabase();
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
}

startApp().catch(console.error);



