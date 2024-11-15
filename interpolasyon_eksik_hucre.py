import pandas as pd
import numpy as np

file_path = 'ana_veri.xlsx'  
weather_data = pd.read_excel(file_path)


weather_data['DateTime'] = pd.to_datetime(weather_data['Date'].astype(str) + ' ' + weather_data['H'].astype(str), errors='coerce', format='%Y-%m-%d %H')
weather_data.set_index('DateTime', inplace=True)
weather_data.drop(columns=['Date', 'H'], inplace=True)


weather_data.dropna(how='all', inplace=True)


weather_data.replace({'—': np.nan, '-': np.nan}, inplace=True)
weather_data['TEMP'] = pd.to_numeric(weather_data['TEMP'].str.replace(' °C', ''), errors='coerce')
weather_data['DWPT'] = pd.to_numeric(weather_data['DWPT'].str.replace(' °C', ''), errors='coerce')
weather_data['PRCP'] = pd.to_numeric(weather_data['PRCP'].str.replace(' mm', ''), errors='coerce')
weather_data['WSPD'] = pd.to_numeric(weather_data['WSPD'].str.replace(' km/h', ''), errors='coerce')
weather_data['PRES'] = pd.to_numeric(weather_data['PRES'].str.replace(' hPa', ''), errors='coerce')
weather_data['RHUM'] = pd.to_numeric(weather_data['RHUM'].str.replace(' %', ''), errors='coerce')


weather_data.interpolate(method='linear', axis=0, inplace=True)


output_path = 'ana_veri_interpolasyon.csv' 
weather_data.to_csv(output_path)

print("Eksik veriler tamamlandı ve yeni dosya kaydedildi:", output_path)
