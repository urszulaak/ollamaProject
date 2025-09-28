import time
from Updater import Updater

class WeatherUpdater(Updater):
    def __init__(self, interval, city, language, labels, weather_panel):
        super().__init__(interval)
        self.city = city
        self.language = language
        self.labels = labels
        self.weather_panel = weather_panel

        self._last_data = None
        self._last_fetch = 0

    def update(self, dt):
        try:
            weather = self.weather_panel.fetch_weather()
            self._last_data = weather
            self._last_fetch = time.time()
        except Exception:
            weather = self._last_data

        if weather:
            self.labels["img"].text = str(weather[0])
            self.labels["temp"].text = str(weather[1])
            self.labels["desc"].text = str(weather[2])