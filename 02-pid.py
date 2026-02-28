import numpy as np
import matplotlib.pyplot as plt

# Hedef: kolu 90 dereceye götür
hedef = 90.0
mevcut_aci = 0.0

# PID katsayıları
Kp = 2.0   # Proportional — hataya ne kadar sert tepki ver
Ki = 0.01  # Integral — birikmiş hatayı düzelt
Kd = 0.1   # Derivative — değişim hızına bak, aşmayı önle

# Simülasyon
dt = 0.1          # zaman adımı (saniye)
sure = 10.0       # toplam süre
adim = int(sure / dt)

hatalar = []
aciler = []
zamanlar = []

integral = 0.0
onceki_hata = 0.0

for i in range(adim):
    t = i * dt
    hata = hedef - mevcut_aci
    integral += hata * dt
    turev = (hata - onceki_hata) / dt

    cikti = Kp * hata + Ki * integral + Kd * turev
    mevcut_aci += cikti * dt

    hatalar.append(hata)
    aciler.append(mevcut_aci)
    zamanlar.append(t)

    onceki_hata = hata

# Grafik
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))

ax1.plot(zamanlar, aciler, 'b-', linewidth=2, label="Mevcut Açı")
ax1.axhline(y=hedef, color='r', linestyle='--', label=f"Hedef ({hedef}°)")
ax1.set_ylabel("Açı (derece)")
ax1.set_title("PID Kontrol — Robotik Kol Açı Takibi")
ax1.legend()
ax1.grid(True)

ax2.plot(zamanlar, hatalar, 'g-', linewidth=2)
ax2.set_ylabel("Hata (derece)")
ax2.set_xlabel("Zaman (sn)")
ax2.set_title("Hata Grafiği")
ax2.grid(True)

plt.tight_layout()
plt.show()