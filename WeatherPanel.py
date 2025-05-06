import python_weather
from datetime import datetime
import asyncio

from enums import languageEnum

class WeatherPanel():

  def __init__(self, city, language):
    self.city = city
    self.language = language

  async def getweather(self) -> list:
    # declare the client. the measuring unit used defaults to the metric system (celcius, km/h, etc.)
    placeholder = []
    async with python_weather.Client(unit=python_weather.METRIC) as client:
      # fetch a weather forecast from a city

      KIND_POLISH_TRANSLATIONS = {
        'Sunny': 'Słonecznie',
        'Partly Cloudy': 'Częściowo Pochmurnie',
        'Cloudy': 'Pochmurnie',
        'Very Cloudy': 'Bardzo Pochmurnie',
        'Fog': 'Mgła',
        'Light Showers': 'Lekkie Przelotne Opady',
        'Light Sleet Showers': 'Lekkie Przelotne Opady Deszczu ze Śniegiem',
        'Light Sleet': 'Lekki Deszcz ze Śniegiem',
        'Thundery Showers': 'Burzowe Przelotne Opady',
        'Light Snow': 'Lekki Śnieg',
        'Heavy Snow': 'Silny Śnieg',
        'Light Rain': 'Lekki Deszcz',
        'Heavy Showers': 'Silne Przelotne Opady',
        'Heavy Rain': 'Silny Deszcz',
        'Light Snow Showers': 'Lekkie Przelotne Opady Śniegu',
        'Heavy Snow Showers': 'Silne Przelotne Opady Śniegu',
        'Thundery Heavy Rain': 'Burzowy Silny Deszcz',
        'Thundery Snow Showers': 'Burzowe Przelotne Opady Śniegu'
      }
      DAYS_POLISH_TRANSLATIONS = {
        'Monday': 'Poneidziałek',
        'Tuesday': 'Wtorek',
        'Wednesday': 'Środa',
        'Thursday': 'Czwartek',
        'Friday': 'Piątek',
        'Saturday': 'Sobota',
        'Sunday': 'Niedziela'
      }
      weather_counts = {}
      weather = await client.get(self.city)
      print(weather.datetime)
      print(weather.country)
      # returns the current day's forecast temperature (int)
      placeholder.append(f"Obecna temperatura: {weather.temperature}°C\n")
      # get the weather forecast for a few days
      for daily in weather:
        day = daily.date.strftime("%A")
        if languageEnum.POLISH:
          placeholder.append(DAYS_POLISH_TRANSLATIONS.get(day, day))
        else:
          placeholder.append(day)
        first_iteration = True
        # hourly forecasts
        for hourly in daily:
          if first_iteration:
            mini = hourly.temperature
            maxi = hourly.temperature
            first_iteration = False
          else:
            if hourly.temperature < mini:
              mini = hourly.temperature
            elif hourly.temperature > maxi:
              maxi = hourly.temperature
          weather_kind = hourly.kind
          if weather_kind in weather_counts:
              weather_counts[weather_kind] += 1
          else:
              weather_counts[weather_kind] = 1
        max_weather = max(weather_counts, key=weather_counts.get)
        placeholder.append(max_weather.emoji)
        if languageEnum.POLISH:
          placeholder.append(KIND_POLISH_TRANSLATIONS.get(str(max_weather), str(max_weather)))
        else:
          placeholder.append(max_weather)
        placeholder.append(f'{maxi} °C / {mini} °C')
        weather_counts = {}
    return placeholder
  
  def fetch_weather(self):
    return asyncio.run(self.getweather())