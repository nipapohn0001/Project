import cv2
import os
import json
from pymongo import MongoClient

# ฟังก์ชันสำหรับการลงทะเบียนผู้เข้าร่วม
def register_attendee(name, frame):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        face_image = frame[y:y+h, x:x+w]
        
        # บันทึกรูปภาพใบหน้า
        face_image_path = f'D:\Project\test{name}.jpg'
        os.makedirs(os.path.dirname(face_image_path), exist_ok=True)
        cv2.imwrite(face_image_path, face_image)
        
        user_data = {
            'name': name,
            'face_image_path': face_image_path  # บันทึกใบหน้าเป็นเส้นทางไฟล์
        }
        register_user(user_data)
        print(f"Registered {name} successfully!")
    else:
        print("No face detected.")

# ฟังก์ชันสำหรับการบันทึกข้อมูลผู้ใช้งานใน MongoDB
def register_user(user_data):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['attendee_database']
    collection = db['attendees']
    collection.insert_one(user_data)
    print("User data inserted into MongoDB successfully!")

# เปิดกล้องสำหรับการลงทะเบียน
video_capture = cv2.VideoCapture(0)
name = input("Enter the name of the attendee: ")

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    # แสดงภาพจากกล้อง
    cv2.imshow('Video - Press "s" to save', frame)

    if cv2.waitKey(1) & 0xFF == ord('s'):
        register_attendee(name, frame)
        break

# ปิดการเชื่อมต่อกล้อง
video_capture.release()
cv2.destroyAllWindows()

# Debug: แสดงไดเรกทอรีทำงานปัจจุบัน
print("Current working directory:", os.getcwd())

# ตรวจสอบเส้นทางไฟล์
image_path = f'D:\Project\test{name}.jpg'  # ใช้ตัวแปร name อย่างถูกต้อง

# Debug: ตรวจสอบว่าไฟล์มีอยู่หรือไม่
if not os.path.isfile(image_path):
    print(f"Error: The file '{image_path}' does not exist.")
else:
    # อ่านภาพ
    image = cv2.imread(image_path)

    # ตรวจสอบว่าภาพถูกโหลดหรือไม่
    if image is None:
        print("Error: ไม่สามารถเปิดหรืออ่านไฟล์ภาพได้")
    else:
        # แสดงภาพ
        cv2.imshow('Test Image', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
