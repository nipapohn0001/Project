const express = require('express');
const bodyParser = require('body-parser');
const MongoClient = require('mongodb').MongoClient;
const app = express();
const PORT = 3000;

app.use(bodyParser.json());

// เชื่อมต่อกับ MongoDB
MongoClient.connect('mongodb://localhost:27017', { useUnifiedTopology: true }, (err, client) => {
  if (err) return console.error(err);
  console.log('Connected to Database');
  const db = client.db('faceRecognition'); // ชื่อฐานข้อมูล
  const studentsCollection = db.collection('students'); // ชื่อ collection

  // ฟังก์ชันคำนวณ Euclidean Distance
  function euclideanDistance(desc1, desc2) {
    let sum = 0;
    for (let i = 0; i < desc1.length; i++) {
      const diff = desc1[i] - desc2[i];
      sum += diff * diff;
    }
    return Math.sqrt(sum);
  }

  // API สำหรับตรวจสอบใบหน้า
  app.post('/recognize', async (req, res) => {
    const { descriptor } = req.body; // faceDescriptor ที่ส่งมาจาก client

    // ดึงข้อมูลนักเรียนทั้งหมดจาก MongoDB
    const students = await studentsCollection.find().toArray();

    let bestMatch = null;
    let minDistance = 0.6; // ค่า threshold ระยะห่างที่ใช้ในการบอกว่าเป็นบุคคลเดียวกัน

    // คำนวณระยะทางระหว่าง faceDescriptor ที่สแกนกับนักเรียนในฐานข้อมูล
    students.forEach(student => {
      const distance = euclideanDistance(descriptor, student.faceDescriptor); // ใช้ฟังก์ชันที่ประกาศไว้
      if (distance < minDistance) {
        bestMatch = student;
        minDistance = distance;
      }
    });

    // ส่งผลลัพธ์กลับไปที่ client
    if (bestMatch) {
      res.status(200).json({
        id: bestMatch.studentId,
        name: bestMatch.name,
        department: bestMatch.department
      });
    } else {
      res.status(404).json({ message: 'No match found' });
    }
  });

  // เปิดเซิร์ฟเวอร์
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
});

app.post('/addStudent', async (req, res) => {
  const { studentId, name, department, faceDescriptor, image } = req.body;

  try {
    const student = {
      studentId,
      name,
      department,
      faceDescriptor,
      image
    };

    await studentsCollection.insertOne(student);
    res.status(201).send('Student added successfully');
  } catch (error) {
    console.error('Error adding student:', error);
    res.status(500).send('Failed to add student');
  }
});

