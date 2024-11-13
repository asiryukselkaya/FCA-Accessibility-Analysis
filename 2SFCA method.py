# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 13:18:08 2024

@author: Aşır Yüksel Kaya
"""
#2SFCA Methot

import pandas as pd
import numpy as np

# Dosyadan veriyi yükleme
file_path = r' Veri Seti'
df = pd.read_excel(file_path)

# Parametreler
d0 = 111  # Mesafe sınırı (örneğin 10 km)
beta = 0.1  # Azaltma fonksiyonu için beta değeri

# Azaltma Fonksiyonu (exponential decay)
def decay_function(distance, beta):
    return np.exp(-beta * distance)

# 1. Adım: Her hastane için R_j hesapla (Hastane Erişilebilirliği)
service_accessibility = {}
for hastane in df['Hastane'].unique():
    # Mesafe sınırı dahilinde olan mahalleleri filtrele
    nearby_demand = df[(df['Hastane'] == hastane) & (df['Distance (KM)'] <= d0)]
    # Ağırlıklı toplam nüfusu hesapla
    weighted_demand_sum = (nearby_demand['Mahalle Nufusu Pk'] * decay_function(nearby_demand['Distance (KM)'], beta)).sum()
    # Erişilebilirlik oranı R_j
    capacity = nearby_demand['Hastane kapasitesi Sj'].iloc[0] if not nearby_demand.empty else 0
    service_accessibility[hastane] = capacity / weighted_demand_sum if weighted_demand_sum > 0 else 0

# 2. Adım: Her mahalle için A_i hesapla (Mahalle Erişilebilirliği)
accessibility_index = {}
for mahalle in df['Mahalle'].unique():
    # Mesafe sınırı dahilinde olan hastaneleri filtrele
    nearby_services = df[(df['Mahalle'] == mahalle) & (df['Distance (KM)'] <= d0)]
    # Ağırlıklı erişilebilirlik indeksini hesapla
    A_i = (nearby_services['Hastane'].map(service_accessibility) * 
           decay_function(nearby_services['Distance (KM)'], beta)).sum()
    accessibility_index[mahalle] = A_i

# Sonuçları en erişilebilirden en erişilemeze göre sıralama
sorted_accessibility = sorted(accessibility_index.items(), key=lambda x: x[1], reverse=True)
sorted_df = pd.DataFrame(sorted_accessibility, columns=['Mahalle', 'Accessibility_Index'])

# Excel dosyasına kaydetme
output_file_path = r'sonuç.xlsx'
sorted_df.to_excel(output_file_path, index=False)

print("Sonuçlar en erişilebilirden en erişilemeze sıralandı ve kaydedildi:", output_file_path)