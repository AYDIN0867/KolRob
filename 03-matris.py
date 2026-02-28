import numpy as np

# Rotasyon matrisi — 2D'de bir noktayı döndür
def rotasyon_matrisi(derece):
    aci = np.radians(derece)
    return np.array([
        [np.cos(aci), -np.sin(aci)],
        [np.sin(aci),  np.cos(aci)]
    ])

# Robotik kolun ucu şu noktada
nokta = np.array([10, 0])  # x=10, y=0

# 45 derece döndür
R = rotasyon_matrisi(45)
yeni_nokta = R @ nokta  # @ işareti = matris çarpımı

print(f"Orijinal nokta : {nokta}")
print(f"45° döndürülmüş: {yeni_nokta.round(2)}")

# Birden fazla dönüşü birleştir
R1 = rotasyon_matrisi(30)
R2 = rotasyon_matrisi(45)
R_toplam = R2 @ R1  # önce 30°, sonra 45° = toplam 75°

sonuc = R_toplam @ nokta
print(f"30°+45° döndürülmüş: {sonuc.round(2)}")

# Kontrol — direkt 75° döndür, aynı sonuç çıkmalı
R75 = rotasyon_matrisi(75)
kontrol = R75 @ nokta
print(f"Direkt 75° döndürülmüş: {kontrol.round(2)}")
print(f"Sonuçlar eşit mi: {np.allclose(sonuc, kontrol)}")