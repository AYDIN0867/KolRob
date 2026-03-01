import cv2

kamera = cv2.VideoCapture(0)  # 0 = bilgisayarın kamerası

while True:
    ret, frame = kamera.read()

    if not ret:
        print("Kamera açılamadı!")
        break

    # Görüntüyü griye çevir
    gri = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Kenar tespiti — Canny algoritması
    kenarlar = cv2.Canny(gri, 50, 150)

    # İkisini yan yana göster
    cv2.imshow("Normal", frame)
    cv2.imshow("Kenarlar", kenarlar)

    # Q tuşuna basınca kapat
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

kamera.release()
cv2.destroyAllWindows()