import numpy as np
import matplotlib.pyplot as plt

# 2 eksenli robotik kol simülasyonu
# L1 = birinci kol uzunluğu, L2 = ikinci kol uzunluğu
L1 = 10
L2 = 7

# Açılar (derece)
theta1 = 90
theta2 = 45

# Forward Kinematics — kolun nerede olduğunu hesapla
t1 = np.radians(theta1)
t2 = np.radians(theta2)

# Eklem noktaları
x1 = L1 * np.cos(t1)
y1 = L1 * np.sin(t1)

x2 = x1 + L2 * np.cos(t1 + t2)
y2 = y1 + L2 * np.sin(t1 + t2)

# Çiz
plt.figure(figsize=(6, 6))
plt.plot([0, x1, x2], [0, y1, y2], 'bo-', linewidth=3, markersize=10)
plt.plot(0, 0, 'rs', markersize=12)  # taban
plt.xlim(-20, 20)
plt.ylim(-20, 20)
plt.grid(True)
plt.title(f"Robotik Kol — theta1={theta1}°, theta2={theta2}°")
plt.show()

print(f"Kolun uç noktası: x={x2:.2f}, y={y2:.2f}")