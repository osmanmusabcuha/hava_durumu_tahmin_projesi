import pandas as pd

file_path = 'ana_veri.xlsx'  
weather_data = pd.read_excel(file_path)

weather_data['DateTime'] = pd.to_datetime(weather_data['Date'].astype(str) + ' ' + weather_data['H'].astype(str), errors='coerce', format='%Y-%m-%d %H')
weather_data.set_index('DateTime', inplace=True)
weather_data.drop(columns=['Date', 'H'], inplace=True)

gece = weather_data.between_time('00:00', '05:59')  
sabah = weather_data.between_time('06:00', '11:59') 
oglen = weather_data.between_time('12:00', '17:59') 
aksam = weather_data.between_time('18:00', '23:59') 

gece.to_csv('gece_verileri.csv')
sabah.to_csv('sabah_verileri.csv')
oglen.to_csv('oglen_verileri.csv')
aksam.to_csv('aksam_verileri.csv')

print("Veriler başarılı bir şekilde zaman dilimlerine göre gruplandı ve kaydedildi.")
