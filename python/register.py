import cv2
import json

# ฟังก์ชันสำหรับการลงทะเบียนผู้เข้าร่วม
def register_attendee(name, frame):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        face_image = frame[y:y+h, x:x+w]
        user_data = {
            'name': name,
            'face_image': face_image.tolist()  # บันทึกใบหน้าเป็นรูปภาพในรูปแบบ list
        }
        register_user(user_data)
        print(f"Registered {name} successfully!")

# ฟังก์ชันสำหรับการบันทึกข้อมูลผู้ใช้งาน
def register_user(user_data):
    with open('registered_users.json', 'a') as f:
        json.dump(user_data, f)
        f.write('\n')

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
