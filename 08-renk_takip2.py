import cv2
import numpy as np

kamera = cv2.VideoCapture(0)
konum_gecmisi = []

while True:
    ret, frame = kamera.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Kırmızı için iki aralık
    alt_sinir1 = np.array([0, 80, 50])
    ust_sinir1 = np.array([15, 255, 255])
    alt_sinir2 = np.array([165, 80, 50])
    ust_sinir2 = np.array([180, 255, 255])

    maske1 = cv2.inRange(hsv, alt_sinir1, ust_sinir1)
    maske2 = cv2.inRange(hsv, alt_sinir2, ust_sinir2)
    maske = cv2.bitwise_or(maske1, maske2)

    maske = cv2.erode(maske, None, iterations=2)
    maske = cv2.dilate(maske, None, iterations=2)

    konturlar, _ = cv2.findContours(maske, cv2.RETR_EXTERNAL,
                                     cv2.CHAIN_APPROX_SIMPLE)

    if konturlar:
        en_buyuk = max(konturlar, key=cv2.contourArea)
        area = cv2.contourArea(en_buyuk)

        if area > 2000:
            (x, y), yaricap = cv2.minEnclosingCircle(en_buyuk)
            merkez = (int(x), int(y))

            # Konumu kaydet
            konum_gecmisi.append(merkez)
            if len(konum_gecmisi) > 50:
                konum_gecmisi.pop(0)

            # Sarı iz çiz
            for i in range(1, len(konum_gecmisi)):
                kalinlik = int(np.sqrt(50 / float(i + 1)) * 2.5)
                cv2.line(frame, konum_gecmisi[i-1], konum_gecmisi[i],
                        (0, 255, 255), kalinlik)

            # Nesnenin etrafına yeşil daire
            cv2.circle(frame, merkez, int(yaricap), (0, 255, 0), 3)
            cv2.circle(frame, merkez, 5, (0, 0, 255), -1)

            # Ekran merkezi — robotik kolun tabanı
            ekran_merkezi = (frame.shape[1]//2, frame.shape[0]//2)
            cv2.circle(frame, ekran_merkezi, 8, (255, 0, 0), -1)

            # Mavi çizgi — merkeze olan mesafe
            mesafe_x = int(x) - ekran_merkezi[0]
            mesafe_y = int(y) - ekran_merkezi[1]
            cv2.line(frame, ekran_merkezi, merkez, (255, 0, 0), 2)

            cv2.putText(frame, f"dx:{mesafe_x} dy:{mesafe_y}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Konum: ({int(x)}, {int(y)})",
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Takip", frame)
    cv2.imshow("Maske", maske)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

kamera.release()
cv2.destroyAllWindows()