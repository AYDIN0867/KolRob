import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import cv2
import threading

# ── Paylaşılan veri ──────────────────────────────────────────────
hedef = {"x": 5.0, "y": 5.0, "z": 5.0}
kol_pos = {"x": 5.0, "y": 5.0, "z": 5.0}

# ── PID ──────────────────────────────────────────────────────────
class PID:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.onceki_hata = 0.0

    def hesapla(self, hedef, mevcut, dt=0.05):
        hata = hedef - mevcut
        self.integral += hata * dt
        turev = (hata - self.onceki_hata) / dt
        self.onceki_hata = hata
        return self.kp * hata + self.ki * self.integral + self.kd * turev

pid_x = PID(3.0, 0.01, 0.5)
pid_y = PID(3.0, 0.01, 0.5)
pid_z = PID(3.0, 0.01, 0.5)  # yeni — derinlik ekseni

# ── 3D Inverse Kinematics ─────────────────────────────────────────
# 3 eklemli kol: omuz, dirsek, bilek
L1 = 10  # omuz → dirsek
L2 = 8   # dirsek → bilek
L3 = 5   # bilek → uç

def ik_3d(tx, ty, tz):
    """
    3D hedef noktasından eklem açılarını hesapla.
    theta1 = yatay dönüş (Z ekseni etrafında)
    theta2 = omuz açısı
    theta3 = dirsek açısı
    """
    # Yatay mesafe — XZ düzleminde
    r = np.sqrt(tx**2 + tz**2)
    r = max(r, 0.1)

    # Yatay dönüş açısı
    theta1 = np.arctan2(tz, tx)

    # Düşey düzlemde 2D IK — r ve ty kullanarak
    dist = np.sqrt(r**2 + ty**2)
    dist = np.clip(dist, 0.1, L1 + L2 - 0.1)

    cos_t3 = (dist**2 - L1**2 - L2**2) / (2 * L1 * L2)
    cos_t3 = np.clip(cos_t3, -1, 1)
    theta3 = np.arccos(cos_t3)

    k1 = L1 + L2 * np.cos(theta3)
    k2 = L2 * np.sin(theta3)
    theta2 = np.arctan2(ty, r) - np.arctan2(k2, k1)

    return theta1, theta2, theta3

def eklem_noktalari(theta1, theta2, theta3):
    """Eklem açılarından 3D koordinatları hesapla"""
    # Omuz → Dirsek
    x1 = L1 * np.cos(theta2) * np.cos(theta1)
    y1 = L1 * np.sin(theta2)
    z1 = L1 * np.cos(theta2) * np.sin(theta1)

    # Dirsek → Bilek
    x2 = x1 + L2 * np.cos(theta2 + theta3) * np.cos(theta1)
    y2 = y1 + L2 * np.sin(theta2 + theta3)
    z2 = z1 + L2 * np.cos(theta2 + theta3) * np.sin(theta1)

    return (x1, y1, z1), (x2, y2, z2)

# ── Kamera Thread ─────────────────────────────────────────────────
def kamera_thread():
    kamera = cv2.VideoCapture(0)

    while True:
        ret, frame = kamera.read()
        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        alt1 = np.array([0, 80, 50])
        ust1 = np.array([15, 255, 255])
        alt2 = np.array([165, 80, 50])
        ust2 = np.array([180, 255, 255])

        maske = cv2.bitwise_or(
            cv2.inRange(hsv, alt1, ust1),
            cv2.inRange(hsv, alt2, ust2)
        )
        maske = cv2.erode(maske, None, iterations=2)
        maske = cv2.dilate(maske, None, iterations=2)

        konturlar, _ = cv2.findContours(maske, cv2.RETR_EXTERNAL,
                                         cv2.CHAIN_APPROX_SIMPLE)
        if konturlar:
            en_buyuk = max(konturlar, key=cv2.contourArea)
            alan = cv2.contourArea(en_buyuk)

            if alan > 2000:
                (x, y), yaricap = cv2.minEnclosingCircle(en_buyuk)

                # X ve Y — kamera pozisyonundan
                hedef["x"] = (x - 320) / 320 * 12
                hedef["y"] = (240 - y) / 240 * 12

                # Z — nesnenin boyutundan derinlik tahmini
                # Büyük nesne = yakın = düşük Z
                # Küçük nesne = uzak = yüksek Z
                hedef["z"] = np.clip(5000 / alan, 1, 12)

                cv2.circle(frame, (int(x), int(y)), int(yaricap), (0, 255, 0), 3)
                cv2.putText(frame, f"X:{hedef['x']:.1f} Y:{hedef['y']:.1f} Z:{hedef['z']:.1f}",
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Alan: {int(alan)} px",
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        cv2.imshow("Kamera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    kamera.release()
    cv2.destroyAllWindows()

# ── 3D Animasyon ──────────────────────────────────────────────────
fig = plt.figure(figsize=(9, 7))
ax = fig.add_subplot(111, projection='3d')

def guncelle(frame_num):
    ax.cla()  # her kareде ekranı temizle

    # PID ile kol pozisyonunu hedefe götür
    kol_pos["x"] += pid_x.hesapla(hedef["x"], kol_pos["x"]) * 0.05
    kol_pos["y"] += pid_y.hesapla(hedef["y"], kol_pos["y"]) * 0.05
    kol_pos["z"] += pid_z.hesapla(hedef["z"], kol_pos["z"]) * 0.05

    # Sınırlar
    kol_pos["x"] = np.clip(kol_pos["x"], -12, 12)
    kol_pos["y"] = np.clip(kol_pos["y"], 0.1, 15)
    kol_pos["z"] = np.clip(kol_pos["z"], 0.1, 12)

    try:
        t1, t2, t3 = ik_3d(kol_pos["x"], kol_pos["y"], kol_pos["z"])
        p1, p2 = eklem_noktalari(t1, t2, t3)

        # Kolu çiz — taban → omuz → dirsek → uç
        xs = [0, p1[0], p2[0], kol_pos["x"]]
        ys = [0, p1[1], p2[1], kol_pos["y"]]
        zs = [0, p1[2], p2[2], kol_pos["z"]]

        ax.plot(xs, ys, zs, 'o-', color='steelblue', linewidth=3, markersize=8)

        # Hedef nokta
        ax.scatter(hedef["x"], hedef["y"], hedef["z"],
                  color='red', s=200, marker='*', label='Hedef')

        # Kol ucu
        ax.scatter(kol_pos["x"], kol_pos["y"], kol_pos["z"],
                  color='green', s=100, label='Kol ucu')

        # Zemin
        ax.plot([-12, 12], [0, 0], [0, 0], color='brown', linewidth=2)

    except:
        pass

    ax.set_xlim(-15, 15)
    ax.set_ylim(0, 20)
    ax.set_zlim(0, 15)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z (Derinlik)')
    ax.set_title('3D Robotik Kol — Kamera Takibi')
    ax.legend()

    return []

# Kamerayı thread'de başlat
t = threading.Thread(target=kamera_thread, daemon=True)
t.start()

ani = animation.FuncAnimation(fig, guncelle, interval=50, blit=False)
plt.show()