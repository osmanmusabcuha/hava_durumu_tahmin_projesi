import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt

file_path = 'ana_veri.xlsx'  
weather_data = pd.read_excel(file_path)


weather_data['DateTime'] = pd.to_datetime(weather_data['Date'].astype(str) + ' ' + weather_data['H'].astype(str), errors='coerce', format='%Y-%m-%d %H')
weather_data.set_index('DateTime', inplace=True)
weather_data.drop(columns=['Date', 'H'], inplace=True)


weather_data['TEMP'] = pd.to_numeric(weather_data['TEMP'].str.replace(' °C', '', regex=False), errors='coerce')
weather_data['DWPT'] = pd.to_numeric(weather_data['DWPT'].str.replace(' °C', '', regex=False), errors='coerce')
weather_data['PRCP'] = pd.to_numeric(weather_data['PRCP'].str.replace(' mm', '', regex=False), errors='coerce')
weather_data['WSPD'] = pd.to_numeric(weather_data['WSPD'].str.replace(' km/h', '', regex=False), errors='coerce')
weather_data['WPGT'] = pd.to_numeric(weather_data['WPGT'].str.replace(' km/h', '', regex=False), errors='coerce')
weather_data['PRES'] = pd.to_numeric(weather_data['PRES'].str.replace(' hPa', '', regex=False), errors='coerce')
weather_data['RHUM'] = pd.to_numeric(weather_data['RHUM'].str.replace(' %', '', regex=False), errors='coerce')


weather_data.fillna(method='ffill', inplace=True)


weather_data_numeric = weather_data.select_dtypes(include=['float64', 'int64'])

weather_data_daily = weather_data_numeric.resample('D').mean()


decomposition = seasonal_decompose(weather_data['TEMP'].dropna(), model='additive', period=24)
trend = decomposition.trend
seasonal = decomposition.seasonal
residual = decomposition.resid


plt.figure(figsize=(12, 10))

plt.subplot(4, 1, 1)
plt.plot(weather_data['TEMP'], label='Orijinal Sıcaklık Verisi')
plt.title('Orijinal Sıcaklık Verisi')
plt.legend(loc='best')

plt.subplot(4, 1, 2)
plt.plot(trend, label='Trend', color='orange')
plt.title('Trend Bileşeni')
plt.legend(loc='best')

plt.subplot(4, 1, 3)
plt.plot(seasonal, label='Mevsimsellik', color='green')
plt.title('Mevsimsellik Bileşeni')
plt.legend(loc='best')

plt.subplot(4, 1, 4)
plt.plot(residual, label='Artıklar', color='red')
plt.title('Artık Bileşeni')
plt.legend(loc='best')

plt.tight_layout()
plt.show()
#Seabold, S., & Perktold, J. (2010). Statsmodels: Econometric and Statistical Modeling with Python. Proceedings of the 9th Python in Science Conference.
#seasonal_decompose fonksiyonu, zaman serisi verilerini analiz etmek için kullanılır ve trend, mevsimsellik (seasonal), ve artık (residual) bileşenlerine ayrıştırır. 