import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading

# ── Paylaşılan veri ──────────────────────────────────────────────
hedef = {"x": 0.0, "y": 5.0}
kol_pos = {"x": 0.0, "y": 5.0}  # kolun şu anki pozisyonu

# ── PID Kontrolcü ────────────────────────────────────────────────
class PIDKontrolcu:
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

pid_x = PIDKontrolcu(kp=3.0, ki=0.01, kd=0.5)
pid_y = PIDKontrolcu(kp=3.0, ki=0.01, kd=0.5)

# ── Inverse Kinematics ───────────────────────────────────────────
L1, L2 = 12, 8

def inverse_kinematics(tx, ty):
    dist = np.sqrt(tx**2 + ty**2)
    dist = np.clip(dist, 0.1, L1 + L2 - 0.1)
    cos_t2 = (dist**2 - L1**2 - L2**2) / (2 * L1 * L2)
    cos_t2 = np.clip(cos_t2, -1, 1)
    t2 = np.arccos(cos_t2)
    k1 = L1 + L2 * np.cos(t2)
    k2 = L2 * np.sin(t2)
    t1 = np.arctan2(ty, tx) - np.arctan2(k2, k1)
    return t1, t2

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
            if cv2.contourArea(en_buyuk) > 2000:
                (x, y), _ = cv2.minEnclosingCircle(en_buyuk)
                hedef["x"] = (x - 320) / 320 * 18
                hedef["y"] = (240 - y) / 240 * 18

                cv2.circle(frame, (int(x), int(y)), 10, (0, 255, 0), 3)
                cv2.putText(frame, f"Hedef: ({hedef['x']:.1f}, {hedef['y']:.1f})",
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Kol: ({kol_pos['x']:.1f}, {kol_pos['y']:.1f})",
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        cv2.imshow("Kamera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    kamera.release()
    cv2.destroyAllWindows()

# ── Animasyon ─────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 7))
kol_cizgi, = ax.plot([], [], 'o-', color='steelblue', linewidth=4, markersize=10)
hedef_nokta, = ax.plot([], [], 'r*', markersize=15, label="Hedef")
kol_nokta, = ax.plot([], [], 'go', markersize=10, label="Kol ucu")

ax.set_xlim(-22, 22)
ax.set_ylim(-5, 25)
ax.set_aspect('equal')
ax.grid(True)
ax.axhline(y=0, color='brown', linewidth=3)
ax.plot(0, 0, 's', color='gray', markersize=15)
ax.legend()
ax.set_title("PID Kontrollü Robotik Kol — Kamera Takibi", fontsize=13)

def guncelle(frame_num):
    # PID ile kol pozisyonunu hedefe yumuşakça götür
    cikti_x = pid_x.hesapla(hedef["x"], kol_pos["x"])
    cikti_y = pid_y.hesapla(hedef["y"], kol_pos["y"])

    kol_pos["x"] += cikti_x * 0.05
    kol_pos["y"] += cikti_y * 0.05

    # Sınırları koru
    kol_pos["x"] = np.clip(kol_pos["x"], -18, 18)
    kol_pos["y"] = np.clip(kol_pos["y"], 0.1, 19)

    try:
        t1, t2 = inverse_kinematics(kol_pos["x"], kol_pos["y"])
        x1 = L1 * np.cos(t1)
        y1 = L1 * np.sin(t1)
        x2 = x1 + L2 * np.cos(t1 + t2)
        y2 = y1 + L2 * np.sin(t1 + t2)

        kol_cizgi.set_data([0, x1, x2], [0, y1, y2])
        hedef_nokta.set_data([hedef["x"]], [hedef["y"]])
        kol_nokta.set_data([x2], [y2])
    except:
        pass

    return kol_cizgi, hedef_nokta, kol_nokta

# Kamerayı thread'de başlat
t = threading.Thread(target=kamera_thread, daemon=True)
t.start()

ani = animation.FuncAnimation(fig, guncelle, interval=50, blit=True)
plt.show()