import time
import httpx
import json
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

class WeatherPanel:
    def __init__(self, city, language):
        with open("APIKeys.json", "r") as f:
            apikeys = json.load(f)
        self.city = city
        self.language = language
        self.API_KEY = apikeys["WeatherAPI"]

        self._last_fetch = 0
        self._cached_data = None

        self.executor = ThreadPoolExecutor(max_workers=1)

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

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, params=params)

                response.raise_for_status()
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
                    placeholder.append(f'{min_temp} °C / {max_temp} °C')
            return placeholder
        
        except httpx.RequestError:
            return None

    def _map_condition_to_emoji(self, description):
        mapping_pl = {
            'Słonecznie': '☀️',
            'Bezchmurnie': '☀️',
            'Częściowe zachmurzenie': '⛅️',
            'Pochmurno': '☁️',
            'Zachmurzenie całkowite': '☁️',
            'Zachmurzenie': '☁️',
            'Mgła': '🌫',
            'Zamglenie': '🌫',
            'Możliwe miejscowe opady deszczu': '🌦',
            'Miejscowe opady deszczu w pobliżu': '🌦',
            'Lekki deszcz': '🌦',
            'Umiarkowany deszcz': '🌧',
            'Silny deszcz': '🌧',
            'Możliwe miejscowe opady śniegu': '🌨',
            'Wiatr ze śniegiem': '🌨',
            'Lekki śnieg': '🌨',
            'Średnie opady śniegu': '🌨',
            'Ciężkie opady śniegu': '❄️',
            'Przejściowe, średnie lub ciężkie opady śniegu': '❄️',
            'Silny śnieg': '❄️',
            'Śniegu w pobliżu': '❄️',
            'Możliwe miejscowe burze': '⛈',
            'Umiarkowany lub silny deszcz z burzą': '⛈',
            'Miejscowy lekki deszcz z burzą': '⛈'
        }
        mapping_en = {
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
        mapping = mapping_pl if self.language == 'pl' else mapping_en
        return mapping.get(description, '✨')

    def fetch_weather(self):
        if time.time() - self._last_fetch < 600 and self._cached_data:
            return self._cached_data

        loop = asyncio.new_event_loop()
        future = self.executor.submit(loop.run_until_complete, self.getweather())
        self._cached_data = future.result()
        self._last_fetch = time.time()
        return self._cached_data
