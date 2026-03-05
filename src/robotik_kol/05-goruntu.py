import cv2
import numpy as np

# Önce kütüphaneyi kuralım — terminale yaz:
# pip install opencv-python

# Basit bir görüntü oluştur — beyaz zemin
goruntu = np.zeros((500, 500, 3), dtype=np.uint8)
goruntu[:] = (255, 255, 255)  # beyaz

# Robotik kol çiz — gerçek OpenCV çizim fonksiyonları
# Taban
cv2.rectangle(goruntu, (225, 450), (275, 480), (100, 100, 100), -1)

# 1. kol
cv2.line(goruntu, (250, 450), (180, 320), (70, 130, 180), 8)
cv2.circle(goruntu, (180, 320), 8, (0, 0, 255), -1)  # eklem

# 2. kol
cv2.line(goruntu, (180, 320), (280, 220), (70, 130, 180), 6)
cv2.circle(goruntu, (280, 220), 8, (0, 0, 255), -1)  # eklem

# 3. kol (gripper)
cv2.line(goruntu, (280, 220), (320, 170), (70, 130, 180), 4)
cv2.circle(goruntu, (320, 170), 10, (0, 0, 200), -1)  # uç

# Yazı ekle
cv2.putText(goruntu, "Ramazan Robotu - OpenCV", (120, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
cv2.putText(goruntu, "Eklem 1", (140, 315),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
cv2.putText(goruntu, "Eklem 2", (285, 215),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
cv2.putText(goruntu, "Gripper", (325, 165),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

cv2.imshow("Robotik Kol", goruntu)
cv2.waitKey(0)
cv2.destroyAllWindows()