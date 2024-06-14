import cv2

# อ่านภาพ
image = cv2.imread('D:/Project/test_cv2/images.jpg')

# ตรวจสอบว่าภาพถูกโหลดหรือไม่
if image is None:
    print("Error: ไม่สามารถเปิดหรืออ่านไฟล์ภาพได้")
else:
    # แสดงภาพ
    cv2.imshow('Test Image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
