import cv2
import os
import pickle
import numpy as np
import face_recognition
import cvzone

# ตั้งค่ากล้อง
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# โหลดภาพพื้นหลัง
imgBackground = cv2.imread('Resources/background.png')
if imgBackground is None:
    print("ไม่สามารถโหลดภาพพื้นหลัง 'Resources/background.png' ได้")
    exit()

# โหลดภาพจากโฟลเดอร์ Modes
folderModePath = 'Resources/Modes'
if not os.path.exists(folderModePath):
    print(f"ไม่พบโฟลเดอร์: {folderModePath}")
    exit()

modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    img = cv2.imread(os.path.join(folderModePath, path))
    if img is not None:
        imgModeList.append(img)
print(f"จำนวนภาพใน imgModeList: {len(imgModeList)}")

# Load the encoding file

print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("Encode File Loaded")

# เริ่มการแสดงภาพ
while True:
    success, img = cap.read()
    if not success:
        print("ไม่สามารถเปิดกล้องได้")
    break

    imgs = cv2.resize(img, (0.0), None, 0.25, 0.25)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgs)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
    
    # เพิ่มภาพจากกล้องลงในพื้นหลัง
    imgBackground[162:162+480, 55:55+640] = img

    # ตรวจสอบว่าภาพใน imgModeList มีเพียงพอที่จะใช้งาน
    if len(imgModeList) > 3:
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[3]

    for encodeFace, faceLoc in zip (encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # print("matches", matches)
        # print("faceDis", faceDis)

        matchIndex = np.argmin(faceDis)
        # print("Match Index", matchIndex)

        if matches[matchIndex]:
            # print("Known Face Detected")
            # print(studentIds[matchIndex])
            y1, x2, y2, x1 = faceLace
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect (imgBackground, bbox, rt = 0)

    
    # cv2.imshow("Webcam", img)
    cv2.imshow("face Attendance", imgBackground)
    cv2.waitKey(1)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
