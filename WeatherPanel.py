import time
import httpx
import json
from datetime import datetime
import asyncio

class WeatherPanel():

  def __init__(self, city, language):
    with open("APIKeys.json", "r") as f:
      apikeys = json.load(f)
    self.city = city
    self.language = language
    self.API_KEY = apikeys["WeatherAPI"]
    self._last_fetch = 0
    self._cached_data = None

  async def getweather(self) -> list:
    placeholder = []

    DAYS_POLISH_TRANSLATIONS = {
        'Monday': 'Poniedziałek',
        'Tuesday': 'Wtorek',
        'Wednesday': 'Środa',
        'Thursday': 'Czwartek',
        'Friday': 'Piątek',
        'Saturday': 'Sobota',
        'Sunday': 'Niedziela'
    }

    url = 'http://api.weatherapi.com/v1/forecast.json'
    params = {
      'key': self.API_KEY,
      'q': self.city,
      'days': 3,
      'lang': self.language,
      'aqi': 'no',
      'alerts': 'no'
    }

    async with httpx.AsyncClient() as client:
      response = await client.get(url, params=params)
      data = response.json()

      current = data['current']
      forecast = data['forecast']['forecastday']

      placeholder.append(self._map_condition_to_emoji(current['condition']['text']))
      placeholder.append(f"{current['temp_c']}°C")
      placeholder.append(f"{current['condition']['text']}")
      
      for day_data in forecast:
        date_obj = datetime.strptime(day_data['date'], '%Y-%m-%d')
        day_name = date_obj.strftime('%A')

        if self.language == 'pl':
          placeholder.append(DAYS_POLISH_TRANSLATIONS.get(day_name, day_name))
        else:
          placeholder.append(day_name)

        condition = day_data['day']['condition']
        description = condition['text']

        max_temp = day_data['day']['maxtemp_c']
        min_temp = day_data['day']['mintemp_c']

        emoji_char = self._map_condition_to_emoji(description)

        placeholder.append(emoji_char)
        placeholder.append(description)
        placeholder.append(f'{max_temp} °C / {min_temp} °C')

    return placeholder

  def _map_condition_to_emoji(self, description):
    if self.language == 'pl':
        mapping = {
        'Słonecznie': '☀️',
        'Bezchmurnie': '☀️',
        'Częściowe zachmurzenie': '⛅️',
        'Pochmurnie': '☁️',
        'Zachmurzenie całkowite': '☁️',
        'Zachmurzenie': '☁️',
        'Mgła': '🌫',
        'Możliwe miejscowe opady deszczu': '🌦',
        'Miejscowe opady deszczu w pobliżu': '🌦',
        'Lekki deszcz': '🌦',
        'Umiarkowany deszcz': '🌧',
        'Silny deszcz': '🌧',
        'Możliwe miejscowe opady śniegu': '🌨',
        'Lekki śnieg': '🌨',
        'Umiarkowany śnieg': '❄️',
        'Silny śnieg': '❄️',
        'Możliwe miejscowe burze': '⛈',
        'Umiarkowany lub silny deszcz z burzą': '⛈',
        'Miejscowy lekki deszcz z burzą': '⛈'
        }
    else:
        mapping = {
        'Sunny': '☀️',
        'Clear': '☀️',
        'Partly Cloudy': '⛅️',
        'Cloudy': '☁️',
        'Overcast': '☁️',
        'Mist': '🌫',
        'Patchy rain possible': '🌦',
        'Patchy rain nearby': '🌦',
        'Light rain': '🌦',
        'Moderate rain': '🌧',
        'Heavy rain': '🌧',
        'Patchy snow possible': '🌨',
        'Light snow': '🌨',
        'Moderate snow': '❄️',
        'Heavy snow': '❄️',
        'Thundery outbreaks possible': '⛈',
        'Moderate or heavy rain with thunder': '⛈',
        'Patchy light rain with thunder': '⛈'
        }
    return mapping.get(description, '✨')

  def fetch_weather(self):
    if time.time() - self._last_fetch < 600 and self._cached_data:
      return self._cached_data
    self._cached_data = asyncio.run(self.getweather())
    self._last_fetch = time.time()
    return self._cached_data
