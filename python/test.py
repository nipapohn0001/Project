import cv2
import os

# Debug: print the current working directory
print("Current working directory:", os.getcwd())

# Verify the file path
image_path = 'D:/Project/test_cv2/images.jpg'

# Debug: check if the file exists
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
