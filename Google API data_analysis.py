# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 15:31:06 2024

@author: Aşır Yüksel KAYA
"""

import os
import sys
import requests
import pandas as pd
import geopandas as gpd  # SHP dosyaları için
import matplotlib.pyplot as plt
import numpy as np

# Google Maps API Key
API_KEY = ' ' # Buraya geçerli Google Maps API anahtarınızı girin

# Dosya yollarını belirtin
ilce_shp_file = r"      "     #Buraya ganaliz edeceğiniz veri setini çekiniz
hospitals_excel_file = r"     "    #Buraya ganaliz edeceğiniz veri setini çekini

# Hastanelerin Excel dosyasını yükleyelim
if os.path.exists(hospitals_excel_file):
    hospitals_df = pd.read_excel(hospitals_excel_file)
    print("Hastaneler Excel dosyası bulundu, devam ediyoruz...")
else:
    print("Hastaneler Excel dosyası bulunamadı, dosya yolunu kontrol edin.")
    sys.exit()

# SHP dosyasını yükleyelim
if os.path.exists(ilce_shp_file):
    ilce_gdf = gpd.read_file(ilce_shp_file)
    print("İlçe SHP dosyası bulundu, devam ediyoruz...")
else:
    print("İlçe SHP dosyası bulunamadı, dosya yolunu kontrol edin.")
    sys.exit()

# Hastane sütun adlarını belirleyelim
hospitals_df.columns = ['Hospital Name', 'Latitude', 'Longitude']

# SHP dosyasındaki ilçe verilerini işlemek
# İlçelerin adı ve koordinat bilgileri ile yeni bir DataFrame oluşturma
ilce_df = pd.DataFrame({
    'Ilce Name': ilce_gdf['Mahalleler'],  # İlçenin adı sütunu
    'Latitude': ilce_gdf['POINT_Y'],      # Enlem sütunu
    'Longitude': ilce_gdf['POINT_X']      # Boylam sütunu
})

# Her ilçe için her hastaneye olan ulaşım sürelerini hesaplamak için bir liste oluşturma
travel_data = []

# Her ilçe için döngü başlatma
for ilce_index, ilce in ilce_df.iterrows():
    # İlçe enlem ve boylamı
    start_lat = ilce['Latitude']
    start_lon = ilce['Longitude']
    ilce_name = ilce['Ilce Name']

    print(f"İlçe: {ilce_name}, Koordinatlar: {start_lat}, {start_lon}")

    # Her ilçeden her hastaneye olan ulaşım süresini hesapla
    for index, hospital in hospitals_df.iterrows():
        hospital_name = hospital["Hospital Name"]
        hospital_lat = hospital["Latitude"]
        hospital_lon = hospital["Longitude"]

        # Google Maps Distance Matrix API URL'si (Araç ile ulaşım)
        routing_url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={start_lat},{start_lon}&destinations={hospital_lat},{hospital_lon}&mode=driving&key={API_KEY}'
        
        # API isteği
        response = requests.get(routing_url)
        route_data = response.json()

        # API anahtarının geçersiz olup olmadığını kontrol et
        if route_data.get('status') == 'REQUEST_DENIED':
            print("Google API anahtarı geçersiz. Lütfen geçerli bir anahtar girin.")
            sys.exit()

        # Rota verisi mevcut değilse hata mesajı göster
        if 'rows' not in route_data or 'elements' not in route_data['rows'][0]:
            print(f"{hospital_name} için rota bilgisi bulunamadı. Hata: {route_data}")
            continue

        # Ulaşım süresi ve mesafeyi saniye ve metre olarak al
        element = route_data['rows'][0]['elements'][0]
        if element['status'] != 'OK':
            print(f"{hospital_name} için geçerli yol bilgisi bulunamadı.")
            continue

        travel_time_seconds = element['duration']['value']
        travel_time_minutes = travel_time_seconds / 60
        distance_meters = element['distance']['value']
        distance_km = distance_meters / 1000

        # İlçe ve hastane arasındaki veriyi tabloya ekle
        travel_data.append({
            "Ilce Name": ilce_name,
            "Hospital Name": hospital_name,
            "Ilce Latitude": start_lat,
            "Ilce Longitude": start_lon,
            "Hospital Latitude": hospital_lat,
            "Hospital Longitude": hospital_lon,
            "Travel Time (Minutes)": travel_time_minutes,
            "Distance (KM)": distance_km
        })

# Veriyi pandas DataFrame formatına çevirme
df_travel_times = pd.DataFrame(travel_data)

# Impedance fonksiyonu için alpha değeri
alpha = 0.01

# Impedance fonksiyonunu hesaplama (örneğin exponential decay fonksiyonu)
df_travel_times['Impedance'] = np.exp(-alpha * df_travel_times['Travel Time (Minutes)'])

# Impedance fonksiyonunu grafikleme
plt.figure(figsize=(8, 6))
plt.plot(df_travel_times['Travel Time (Minutes)'], df_travel_times['Impedance'], label='Impedance Function')
plt.xlabel('Access Time (Minutes)')
plt.ylabel('Impedance (Strength of Potential Energy)')
plt.title('Impedance Function Over Access Time')
plt.grid(True)
plt.show()

# Veriyi Excel dosyasına kaydetme
output_file = r"Transportt_Impedance_Travel_Times.xlsx"
df_travel_times.to_excel(output_file, index=False)
print(f"Impedance verisi Excel dosyasına kaydedildi: {output_file}")

# taleb edilmesi halinde veri seti paylaşılacaktır.
