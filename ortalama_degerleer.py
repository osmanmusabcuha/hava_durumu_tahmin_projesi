import pandas as pd
import matplotlib.pyplot as plt

file_path = 'ana_veri.xlsx'
weather_data = pd.read_excel(file_path)

weather_data['TEMP'] = pd.to_numeric(weather_data['TEMP'].str.replace(' °C', ''), errors='coerce')

weather_data['Datetime'] = pd.to_datetime(weather_data['Date'] + ' ' + weather_data['H'], errors='coerce', format='%Y-%m-%d %H')
weather_data.set_index('Datetime', inplace=True)


weather_data.dropna(subset=['TEMP'], inplace=True)

daily_avg = weather_data[['TEMP']].resample('D').mean()
weekly_avg = weather_data[['TEMP']].resample('W').mean()
monthly_avg = weather_data[['TEMP']].resample('M').mean()

plt.figure(figsize=(12, 8))

plt.subplot(3, 1, 1)
plt.plot(daily_avg.index, daily_avg['TEMP'], label='Günlük Ortalama Sıcaklık', color='b')
plt.title('Günlük Ortalama Sıcaklık')
plt.ylabel('Sıcaklık (°C)')
plt.legend()

plt.subplot(3, 1, 2)
plt.plot(weekly_avg.index, weekly_avg['TEMP'], label='Haftalık Ortalama Sıcaklık', color='g')
plt.title('Haftalık Ortalama Sıcaklık')
plt.ylabel('Sıcaklık (°C)')
plt.legend()

plt.subplot(3, 1, 3)
plt.plot(monthly_avg.index, monthly_avg['TEMP'], label='Aylık Ortalama Sıcaklık', color='r')
plt.title('Aylık Ortalama Sıcaklık')
plt.xlabel('Tarih')
plt.ylabel('Sıcaklık (°C)')
plt.legend()

plt.tight_layout()
plt.show()
