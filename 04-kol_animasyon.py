import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

L1 = 10  # 1. kol uzunluğu
L2 = 7   # 2. kol uzunluğu
L3 = 4   # 3. kol uzunluğu (el/gripper)

fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(-25, 25)
ax.set_ylim(-25, 25)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title("3 Eklemli Robotik Kol Simülasyonu", fontsize=14)

# Zemin çizgisi
ax.axhline(y=0, color='brown', linewidth=3)
ax.plot(0, 0, 's', color='gray', markersize=15)  # taban

kol, = ax.plot([], [], 'o-', color='steelblue', linewidth=4, markersize=10)
gripper, = ax.plot([], [], 's', color='red', markersize=12)  # uç
iz, = ax.plot([], [], '--', color='lightblue', linewidth=1, alpha=0.5)

iz_x, iz_y = [], []

def guncelle(frame):
    # Açılar zamanla değişiyor — gerçek robot hareketi gibi
    t1 = np.radians(45 + 30 * np.sin(np.radians(frame)))
    t2 = np.radians(30 + 40 * np.sin(np.radians(frame * 1.5)))
    t3 = np.radians(20 + 20 * np.sin(np.radians(frame * 2)))

    # Eklem konumları
    x1 = L1 * np.cos(t1)
    y1 = L1 * np.sin(t1)

    x2 = x1 + L2 * np.cos(t1 + t2)
    y2 = y1 + L2 * np.sin(t1 + t2)

    x3 = x2 + L3 * np.cos(t1 + t2 + t3)
    y3 = y2 + L3 * np.sin(t1 + t2 + t3)

    kol.set_data([0, x1, x2, x3], [0, y1, y2, y3])
    gripper.set_data([x3], [y3])

    iz_x.append(x3)
    iz_y.append(y3)
    iz.set_data(iz_x[-100:], iz_y[-100:])  # son 100 nokta

    return kol, gripper, iz

ani = animation.FuncAnimation(fig, guncelle, frames=360,
                               interval=30, blit=True)
plt.tight_layout()
plt.show()