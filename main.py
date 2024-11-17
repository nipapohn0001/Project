import cv2
import os
import pickle
import numpy as np
import face_recognition
import cvzone
from datetime import datetime
from mongo_backend import AttendanceDB

class AttendanceUI:
    def __init__(self):
        self.mode = "ACTIVE"
        self.student_info = None
        self.status_color = (255, 255, 255)
        self.detected_faces = []  # เก็บข้อมูลใบหน้าที่ตรวจพบทั้งหมด
        
    def draw_status(self, img, status_text, pos, color=(255, 255, 255)):
        cv2.rectangle(img, (808, pos[1]-20), (808+414, pos[1]+40), 
                     (196, 156, 248), cv2.FILLED)
        cv2.putText(img, status_text, (pos[0], pos[1]+10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    def draw_student_info(self, img, student_data, index=0):
        if student_data:
            try:
                # คำนวณตำแหน่ง Y ตามลำดับของใบหน้า
                base_y = 460 + (index * 100)  # เพิ่มระยะห่าง 100 พิกเซลต่อคน
                
                # วาดพื้นหลังสำหรับข้อมูลแต่ละคน
                cv2.rectangle(img, (808, base_y-30), (808+414, base_y+60), 
                            (255, 255, 255), cv2.FILLED)
                
                # แสดง ID นักศึกษา
                id_text = f"ID: {student_data.get('student_id', 'N/A')}"
                cv2.putText(img, id_text, 
                           (808+10, base_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 
                           (0, 0, 0), 2)
                
                # แสดงสาขา - แก้ไขการแสดงผลภาษาไทย
                major = student_data.get('major', 'N/A')
                major_text = f"Major: {major}"
                # ใช้ font FONT_HERSHEY_COMPLEX สำหรับการแสดงผลภาษาไทย
                cv2.putText(img, major_text.encode('cp874').decode('cp874'), 
                           (808+10, base_y+30), cv2.FONT_HERSHEY_COMPLEX, 0.8, 
                           (0, 0, 0), 2)
                
                # แสดงเวลา
                current_time = datetime.now().strftime("%H:%M:%S")
                cv2.putText(img, f"Time: {current_time}", 
                           (808+10, base_y+60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 
                           (0, 0, 0), 2)
                
            except Exception as e:
                print(f"Error drawing student info: {str(e)}")

    def update_detected_faces(self, student_data):
        """อัพเดตรายการใบหน้าที่ตรวจพบ"""
        if student_data:
            student_id = student_data.get('student_id')
            if student_id not in [face.get('student_id') for face in self.detected_faces]:
                self.detected_faces.append(student_data)
            # จำกัดจำนวนใบหน้าที่แสดง
            if len(self.detected_faces) > 3:  # แสดงสูงสุด 3 คน
                self.detected_faces.pop(0)

def main():
    db = AttendanceDB()
    ui = AttendanceUI()
    
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    imgBackground = cv2.imread('Resources/background.png')
    if imgBackground is None:
        print("Error: ไม่สามารถโหลดภาพพื้นหลังได้")
        return
    
    # โหลดภาพจาก Modes
    folderModePath = 'Resources/Modes'
    if not os.path.exists(folderModePath):
        print(f"Error: ไม่พบโฟลเดอร์ {folderModePath}")
        return
        
    modePathList = os.listdir(folderModePath)
    imgModeList = []
    for path in modePathList:
        img = cv2.imread(os.path.join(folderModePath, path))
        if img is not None:
            imgModeList.append(img)

    try:
        print("Loading Encode File ...")
        file = open('EncodeFile.p', 'rb')
        encodeListKnownWithIds = pickle.load(file)
        file.close()
        encodeListKnown, studentIds = encodeListKnownWithIds
        print("Encode File Loaded")
    except Exception as e:
        print(f"Error loading encode file: {str(e)}")
        return

    counter = 0
    previous_id = None
    attendance_recorded = False

    while True:
        success, img = cap.read()
        if not success:
            print("Error: ไม่สามารถอ่านภาพจากกล้องได้")
            break

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
        
        imgBackground[162:162+480, 55:55+640] = img

        if len(faceCurFrame) == 0:
            ui.mode = "ACTIVE"
            ui.detected_faces = []  # เคลียร์รายการเมื่อไม่พบใบหน้า
        
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            if len(faceDis) > 0:
                matchIndex = np.argmin(faceDis)
                
                if matches[matchIndex]:
                    current_id = studentIds[matchIndex]
                    
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                    
                    if current_id != previous_id:
                        counter = 0
                        attendance_recorded = False
                        previous_id = current_id
                        try:
                            student_data = db.get_student(current_id)
                            ui.update_detected_faces(student_data)  # อัพเดตรายการใบหน้า
                            ui.mode = "SCANNING"
                        except Exception as e:
                            print(f"Error getting student data: {str(e)}")
                            ui.mode = "ERROR"
                    
                    if not attendance_recorded:
                        counter += 1
                        if counter >= 10:
                            try:
                                result = db.record_attendance(current_id)
                                if result.get("status") == "success":
                                    ui.mode = "MARKED"
                                    attendance_recorded = True
                                else:
                                    if result.get("message", "").lower().find("already marked") != -1:
                                        ui.mode = "ALREADY_MARKED"
                                    else:
                                        ui.mode = "ERROR"
                            except Exception as e:
                                print(f"Error recording attendance: {str(e)}")
                                ui.mode = "ERROR"

        # แสดงสถานะ
        if ui.mode == "ACTIVE":
            ui.draw_status(imgBackground, "ACTIVE", (900, 100))
        elif ui.mode == "SCANNING":
            ui.draw_status(imgBackground, "SCANNING...", (900, 100), (255, 255, 0))
        elif ui.mode == "MARKED":
            ui.draw_status(imgBackground, "MARKED", (900, 100), (0, 255, 0))
        elif ui.mode == "ALREADY_MARKED":
            ui.draw_status(imgBackground, "ALREADY MARKED", (900, 100), (0, 0, 255))
        elif ui.mode == "ERROR":
            ui.draw_status(imgBackground, "ERROR", (900, 100), (0, 0, 255))

        # แสดงข้อมูลนักศึกษาทั้งหมดที่ตรวจพบ
        for i, student_data in enumerate(ui.detected_faces):
            ui.draw_student_info(imgBackground, student_data, i)

        cv2.imshow("Face Attendance", imgBackground)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()