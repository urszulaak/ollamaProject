import python_weather
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

      KIND_TRANSLATIONS = {
          'sunny': '☀️',
          'partly cloudy': '⛅',
          'very cloudy': '☁️',
          'light showers': '🌦️',
          'fog': '🌫️'
      }
      KIND_POLISH_TRANSLATIONS = {
          'sunny': 'słonecznie',
          'partly cloudy': 'częściowo pochmurnie',
          'very cloudy': 'bardzo pochmurnie',
          'light showers': 'lekkie opady',
          'fog': 'mgła'
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
      
      # returns the current day's forecast temperature (int)
      placeholder.append(f"Obecna temperatura: {weather.temperature}°C\n")
      
      # get the weather forecast for a few days
      for daily in weather:
        placeholder.append(daily.date.strftime("%A"))
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
          weather_kind = str(hourly.kind).lower()
          if weather_kind in weather_counts:
              weather_counts[weather_kind] += 1
          else:
              weather_counts[weather_kind] = 1
        max_weather = max(weather_counts, key=weather_counts.get)
        desc = KIND_TRANSLATIONS.get(max_weather, 'X')
        placeholder.append(desc)
        if languageEnum.POLISH:
          placeholder.append(KIND_POLISH_TRANSLATIONS.get(max_weather, max_weather))
        else:
          placeholder.append(max_weather)
        placeholder.append(f'{"W:" if languageEnum.POLISH else "H:"} {maxi} °C')
        placeholder.append(f'{"N:" if languageEnum.POLISH else "L:"} {mini} °C')
        weather_counts = {}
    return placeholder
  
  def fetch_weather(self):
    return asyncio.run(self.getweather())