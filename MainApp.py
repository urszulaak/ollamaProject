from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.text import LabelBase
from VoiceRecord import VoiceRecord
from OllamaGen import OllamaGen
from datetime import datetime
from Updater import Updater
from WeatherUpdater import WeatherUpdater
from WeatherPanel import WeatherPanel
from enums import typeEnum, languageEnum
import subprocess
import threading
import os

LabelBase.register(name="EmojiFont", fn_regular="NotoColorEmoji.ttf")

MODELS = {
    languageEnum.ENGLISH: {
        "vosk": "vosk-model-en-us-0.22-lgraph",
        "ai": {
            "ollama_model": "llama3.1:8b",
            "note": "./system_note_eng.txt"
        },
        "espeak": "en-gb",
        "record": "Recording...",
        "lang": "en",
        "info": {
            "start": "start - start conversation with AI\nweather - detailed weather forecat",
            "stop": "stop - end of sentence\nexit - end chat"
        },
        "no_connection": "No internet connection"
    },
    languageEnum.POLISH: {
        "vosk": "vosk-model-small-pl-0.22",
        "ai": {
            "ollama_model": "SpeakLeash/bielik-11b-v2.3-instruct:Q4_K_M",
            "note": "./system_note_pl.txt"
        },
        "espeak": "pl",
        "record": "Nagrywanie...",
        "lang": "pl",
        "info": {
            "start": "start - rozpocznij rozmowę z AI\npogoda - wyświetl szczegółową prognozę pogody",
            "stop": "stop - koniec sekwencji\nkoniec - koniec rozmowy"
        },
        "no_connection": "Brak dostępu do internetu"
    },
}

class MyLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_history = []
        self.language = languageEnum.POLISH
        self.config = MODELS[self.language]
        self.model_path = self.config["vosk"]
        self.model_ai = self.config["ai"]
        self.espeak_lang = self.config["espeak"]
        self.recording = self.config["record"]
        self.collect_chunk = []
        self.voice_recorder = VoiceRecord()
        self.model_generate = OllamaGen()
        self.img_animation_event = None
        self.img_animation_index = 0
        self.img_animation_sources = ["mask_O.png", "mask_half_smile.png", "mask_full_smile.png"]
        self.punctuation = ["i", "a", "ale", "lecz", "lub", "czy", "więc", "zatem", "natomiast","że", "ponieważ", "gdy", "kiedy", "jeśli", "chociaż", "aby", "który", "która", "które"]
        self.punctuation_mark = [".", "!", "?", ",", "-"]
        self.fisrt_sentence = False
        self.no_connection = False

    def change_img(self, name):
        self.ids.face_img.source = name
        self.ids.face_img.reload()

    def start_img_animation(self):
        if self.img_animation_event:
            return
        self.img_animation_index = 0
        self.img_animation_event = Clock.schedule_interval(self._animate_img_step, 0.2)

    def _animate_img_step(self, dt):
        if not self.collect_chunk:
            self.stop_img_animation()
            return

        source = self.img_animation_sources[self.img_animation_index]
        self.ids.face_img.source = source
        self.ids.face_img.reload()
        self.img_animation_index = (self.img_animation_index + 1) % len(self.img_animation_sources)

    def stop_img_animation(self):
        if self.img_animation_event:
            self.img_animation_event.cancel()
            self.img_animation_event = None
            Clock.schedule_once(lambda dt: self.change_img("mask_full_smile.png"))

    def onRecognitionResult(self, recognized_text, status, end):
        if end:
            if status == typeEnum.START:
                for col_id in ['col1', 'col2', 'col3']:
                    self.ids[f'{col_id}_img'].text = str("")
                    self.ids[f'{col_id}_day'].text = str("")
                    self.ids[f'{col_id}_desc'].text = str("")
                    self.ids[f'{col_id}_H'].text = str("")
                self.ids.columns.size_hint_y = 0.2
                self.ids.model_response.size_hint_y = 0.6
                self.chat_history.clear()
                self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config["info"], typeEnum.START.value)
                self.ids.command.text = self.recording
                self.voice_recorder.voiceRecord(self.onRecognitionResult, True)
            elif status == typeEnum.STOP:
                user_message = recognized_text.rsplit(' ', 1)[0]
                self.ids.command.text = user_message
                Clock.schedule_once(lambda dt: self.change_img("mask_think.png"))
                self.chat_history.append({"role": "user", "content": user_message})
                print("yyyyyyyyyyyyyy")
                print(self.chat_history)
                print("yyyyyyyyyyyyyy")
                self.model_generate.GenerateRespond(self.ids.command.text, self.model_ai, self.onModelGenerate, chat_history=self.chat_history)
            elif status == typeEnum.END:
                self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config["info"])
                self.ids.command.text = ""
                self.ids.model_response.text = ""
                self.chat_history.clear()
                self.voice_recorder.voiceRecord(self.onRecognitionResult)
            elif status == typeEnum.WEATHER:
                weather_panel = WeatherPanel("Bialystok", self.config["lang"])
                self.weather = weather_panel.fetch_weather()
                if self.no_connection:
                    self.ids.model_response.text =  self.config["no_connection"]
                else:
                    self.ids.model_response.size_hint_y = 0.2
                    self.ids.columns.size_hint_y = 0.6
                    columns = [
                        ('col1', 3, 4, 5, 6),
                        ('col2', 7, 8, 9, 10),
                        ('col3', 11, 12, 13, 14)
                    ]
                    for col_id, day_idx, img_idx, desc_idx, high_idx in columns:
                        self.ids[f'{col_id}_img'].text = str(self.weather[img_idx])
                        self.ids[f'{col_id}_day'].text = str(self.weather[day_idx])
                        self.ids[f'{col_id}_desc'].text = str(self.weather[desc_idx])
                        self.ids[f'{col_id}_H'].text = str(self.weather[high_idx])
                    self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config["info"])
                    self.voice_recorder.voiceRecord(self.onRecognitionResult)
        else:
            self.ids.command.text = recognized_text

    def speak(self, sentence):
        self.start_img_animation()
        os.system(f"espeak -v {self.espeak_lang} '{sentence}'")
        self.stop_img_animation()

    def onModelGenerate(self, answer, chunk, end):
            if chunk:
                if not self.fisrt_sentence:
                    self.collect_chunk.append(chunk)
                    if chunk[-1] in self.punctuation_mark:
                        self.fisrt_sentence = True
                        sentence = ' '.join(ch for ch in self.collect_chunk)
                        self.ids.model_response.text = answer[:answer.rfind(" ")]
                        self.speak(sentence)
                        self.collect_chunk.clear()
                else:
                    self.collect_chunk.append(chunk)
                    if chunk in self.punctuation or chunk[-1] in self.punctuation_mark:
                        if chunk in self.punctuation:
                            self.collect_chunk.pop()
                        sentence = ' '.join(ch for ch in self.collect_chunk)
                        self.speak(sentence)
                        self.collect_chunk.clear()
                        if chunk in self.punctuation:
                            self.collect_chunk.append(chunk)
            else:
                if self.fisrt_sentence:
                    self.ids.model_response.text = answer
                    if end:
                        self.chat_history.append({"role": "assistant", "content": answer})
                        print(self.chat_history)
                        if self.collect_chunk:
                            sentence = ' '.join(self.collect_chunk)
                            self.speak(sentence)
                        self.fisrt_sentence = False
                        self.onRecognitionResult("", typeEnum.START, True)

    def update_time(self):
        now = datetime.now()
        self.ids.time.text = now.strftime("%H:%M")
        self.ids.date.text = now.strftime("%d.%m.%Y")

    def open(self, dt):
        self.info = self.voice_recorder.voiceInitial(self.model_path, self.config["info"])
        self.ids.header.text = self.info
        self.time_updater = Updater(
            1, 
            strategy=lambda: self.update_time()
        )
        self.time_updater.start()

        self.weather_updater = WeatherUpdater(
            3600,
            "Bialystok",
            self.config["lang"],
            {
                "img": self.ids.weather_img,
                "temp": self.ids.weather_H,
                "desc": self.ids.weather_desc
            },
            WeatherPanel("Bialystok", self.config["lang"])
        )
        self.weather_updater.start()
        self.voice_recorder.voiceRecord(self.onRecognitionResult)

class MyApp(App):

    def build(self):
        myLayout = MyLayout()
        Clock.schedule_once(myLayout.open,0)
        return myLayout

if __name__ == "__main__":
    MyApp().run()
