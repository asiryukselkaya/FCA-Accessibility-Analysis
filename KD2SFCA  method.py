# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 13:43:08 2024

@author: Aşır Yüksel Kaya
"""

import pandas as pd
import numpy as np
# KD2SFCA Method

# Dosyadan veriyi yükleme
data  = pd.read_excel (r'veri Seti.xlsx')

# Parametreler
travel_time_threshold = 222  # Seyahat süresi eşiği (dakika)
decay_factor = 0.1          # Azalma fonksiyonu için bir katsayı

# 2. Adım: Gaussian Azalma Fonksiyonu
def gaussian_decay(travel_time, d0, decay_factor=0.1):
    if travel_time <= d0:
        return np.exp(-decay_factor * travel_time)
    else:
        return 0

# 3. Adım: Her hastane için arz değeri (D_j) hesaplama
hospital_supply = {}
for hospital in data['Hastane'].unique():
    hospital_data = data[(data['Hastane'] == hospital) & (data['Otobüs'] <= travel_time_threshold)]
    S_j = data.loc[data['Hastane'] == hospital, 'Hastane kapasitesi Sj'].values[0]
    
    # Gaussian azaltma fonksiyonunu uygulayarak nüfus ile çarpıyoruz
    decay_population_sum = sum(hospital_data.apply(lambda x: gaussian_decay(x['Otobüs'], travel_time_threshold, decay_factor), axis=1) * hospital_data['Mahalle Nufusu Pk'])
    
    # Sıfır bölme hatasından kaçınmak için kontrol ekliyoruz
    if decay_population_sum > 0:
        D_j = S_j / decay_population_sum
    else:
        D_j = 0  # Eğer toplam sıfırsa, D_j değerini sıfır olarak ayarla
    
    hospital_supply[hospital] = D_j

# 4. Adım: Her mahalle için erişilebilirlik (A_i) hesaplama
accessibility = {}
for region in data['Mahalle'].unique():
    region_data = data[(data['Mahalle'] == region) & (data['Otobüs'] <= travel_time_threshold)]
    A_i = sum(region_data.apply(lambda x: hospital_supply[x['Hastane']] * gaussian_decay(x['Sure dk,j'], travel_time_threshold, decay_factor), axis=1))
    accessibility[region] = A_i

# Sonuçları bir DataFrame'e dönüştürme
accessibility_df = pd.DataFrame(list(accessibility.items()), columns=['Mahalle', 'accessibility_score'])

# Sonuçları yazdır
print(accessibility_df)

output_file_path = r'sonuç.xlsx'
accessibility_df.to_excel(output_file_path, index=False)

print("Erişilebilirlik sonuçları şu dosyaya kaydedildi:", output_file_path)