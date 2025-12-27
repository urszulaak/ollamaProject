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
from RSSPanel import RSSUpdater
from enums import typeEnum, languageEnum
import os
import json

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
            "start": "start - start conversation with AI\nweather - detailed weather forecat\nnews - NBC News",
            "stop": "stop - end of sentence\nclear - clear sentence\nexit - end chat",
            "news": "next - next news\n previous - previous news\n expand - expand news\nexit - exit news\nstart conversation with AI\nweather - detailed weather forecat"
        },
        "commands": {
            "start": typeEnum.START,
            "stop": typeEnum.STOP,
            "end": typeEnum.END,
            "weather": typeEnum.WEATHER,
            "news": typeEnum.NEWS,
            "expand": typeEnum.EXPAND_NEWS,
            "next": typeEnum.NEXT_NEWS,
            "previous": typeEnum.PREVIOUS_NEWS
        },
        "aiCommands": {
            "start": typeEnum.START,
            "stop": typeEnum.STOP,
            "exit": typeEnum.END,
            "clear": "CLEAR_BUFFER"
        },
        "no_connection": "No internet connection",
        "punctuation_words": ["and", "but", "or", "so", "because", "that", "which", "who", "who", "if", "when", "although", "while", "since", "however", "therefore"]
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
            "start": "start - rozpocznij rozmowę z AI\npogoda - wyświetl szczegółową prognozę pogody\nwiadomości - Wiadomości Kurier Poranny",
            "stop": "stop - koniec sekwencji\nwyczyść - wyczyść sekwencje\nkoniec - koniec rozmowy",
            "news": "następna - następna wiadomość\npoprzednia - poprzednia wiadomość\n rozwiń - rozwiń wiadomość\nkoniec - zamknij wiadomość\nstart - rozpocznij rozmowę z AI\npogoda - wyświetl szczegółową prognozę pogody"
        },
        "commands": {
            "start": typeEnum.START,
            "stop": typeEnum.STOP,
            "koniec": typeEnum.END,
            "pogoda": typeEnum.WEATHER,
            "wiadomości": typeEnum.NEWS,
            "rozwiń": typeEnum.EXPAND_NEWS,
            "następna": typeEnum.NEXT_NEWS,
            "poprzednia": typeEnum.PREVIOUS_NEWS
        },
        "aiCommands": {
            "start": typeEnum.START,
            "stop": typeEnum.STOP,
            "koniec": typeEnum.END,
            "wyczyść": "CLEAR_BUFFER"
        },
        "no_connection": "Brak dostępu do internetu",
        "punctuation_words": ["i", "a", "ale", "lecz", "lub", "czy", "więc", "zatem", "natomiast","że", "ponieważ", "gdy", "kiedy", "jeśli", "chociaż", "aby", "który", "która", "które"]
    },
}

class MyLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open("settings.json", "r") as f:
            infos = json.load(f)
        lang = infos["Language"]
        self.language = languageEnum[lang]
        self.city = infos["City"]
        self.chat_history = []
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
        self.news_index = 0
        self.img_animation_sources = ["mask_O.png", "mask_half_smile.png", "mask_full_smile.png"]
        self.punctuation = self.config["punctuation_words"]
        self.punctuation_mark = [".", "!", "?", ",", "-"]
        self.fisrt_sentence = False
        self.no_connection = False
        self.expanded_news = False
        self.news_view = False
        self.ai_view = False

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
                self.ids.content.size_hint_y = 0.5
                self.ids.image_box.size_hint_y = 0.35
                self.ids.columns.size_hint_y = 0.2
                self.ids.model_response.size_hint_y = 0.6
                self.ids.face_img.size_hint_y=1
                self.ai_view = True
                self.ids.model_response.text = ""
                self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config, typeEnum.START.value)
                self.ids.command.text = self.recording
                self.voice_recorder.voiceRecord(self.onRecognitionResult, True)
            elif status == typeEnum.STOP and self.ai_view:
                Clock.schedule_once(lambda dt: self.change_img("mask_think.png"),0)
                user_message = recognized_text.rsplit(' ', 1)[0]
                self.ids.command.text = user_message
                self.chat_history.append({"role": "user", "content": user_message})
                self.model_generate.GenerateRespond(self.ids.command.text, self.model_ai, self.rss_panel.data, self.onModelGenerate, chat_history=self.chat_history)
            elif status == typeEnum.END:
                if self.ai_view:
                    self.ai_view = False
                else:
                    self.news_view = False
                    self.expanded_news = False
                self.ids.content.size_hint_y = 0.5
                self.ids.image_box.size_hint_y = 0.35
                self.ids.model_response.size_hint_y = 0.2
                self.ids.columns.size_hint_y = 0.6
                self.ids.face_img.size_hint_y=0
                self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config)
                self.ids.command.text = ""
                self.ids.model_response.text = ""
                self.chat_history.clear()
                self.voice_recorder.voiceRecord(self.onRecognitionResult)
            elif status == typeEnum.WEATHER and not self.ai_view:
                self.weather = self.weather_updater._last_data
                if self.weather is None:
                    self.ids.model_response.text =  self.config["no_connection"]
                    self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config)
                else:
                    self.ids.model_response.size_hint_y = 0.2
                    self.ids.columns.size_hint_y = 0.6
                    self.ids.face_img.size_hint_y=0
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
                    if self.news_view:
                        self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config, typeEnum.NEWS.value)
                    else:
                        self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config)
                self.voice_recorder.voiceRecord(self.onRecognitionResult)
            elif status == typeEnum.NEWS and not self.ai_view:
                if not self.rss_panel.data:
                    self.ids.model_response.text =  self.config["no_connection"]
                    self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config)
                else:
                    self.news_view = True
                    self.ids.model_response.size_hint_y = 0.2
                    self.ids.columns.size_hint_y = 0.6
                    self.ids.face_img.size_hint_y=0
                    self.rss_dict = self.rss_panel.data
                    self.news = list(self.rss_dict.keys())
                    self.actuall_news = self.news[self.news_index]
                    self.ids.model_response.text = self.actuall_news
                    self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config, typeEnum.NEWS.value)
                self.voice_recorder.voiceRecord(self.onRecognitionResult)
            elif status == typeEnum.EXPAND_NEWS and self.news_view:
                self.expanded_news = True
                self.ids.content.size_hint_y = 0.75
                self.ids.image_box.size_hint_y = 0.1
                self.ids.model_response.size_hint_y = 0.45
                self.ids.columns.size_hint_y = 0.35
                self.ids.face_img.size_hint_y=0
                self.ids.model_response.text = f"{self.actuall_news}\n\n{self.rss_dict[self.actuall_news]}"
                self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config, typeEnum.NEWS.value)
                self.voice_recorder.voiceRecord(self.onRecognitionResult)
            elif status == typeEnum.NEXT_NEWS and self.news_view:
                if self.news_index < len(self.news) - 1:
                    self.news_index +=1
                    self.actuall_news = self.news[self.news_index]
                self.ids.face_img.size_hint_y=0
                def update_news(dt):
                    if self.expanded_news:
                        self.ids.model_response.text = f"{self.actuall_news}\n\n{self.rss_dict[self.actuall_news]}"
                    else:
                        self.ids.model_response.text = self.actuall_news
                Clock.schedule_once(update_news)
                self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config, typeEnum.NEWS.value)
                self.voice_recorder.voiceRecord(self.onRecognitionResult)
            elif status == typeEnum.PREVIOUS_NEWS and self.news_view:
                if self.news_index > 0:
                    self.news_index -=1
                    self.actuall_news = self.news[self.news_index]
                self.ids.face_img.size_hint_y=0
                def update_news(dt):
                    if self.expanded_news:
                        self.ids.model_response.text = f"{self.actuall_news}\n\n{self.rss_dict[self.actuall_news]}"
                    else:
                        self.ids.model_response.text = self.actuall_news
                Clock.schedule_once(update_news)
                self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config, typeEnum.NEWS.value)
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
        self.ids.face_img.size_hint_y = 0
        self.info = self.voice_recorder.voiceInitial(self.model_path, self.config)
        self.ids.header.text = self.info
        self.time_updater = Updater(
            1, 
            strategy=lambda: self.update_time()
        )
        self.time_updater.start()

        self.weather_updater = WeatherUpdater(
            3600,
            self.city,
            self.config["lang"],
            {
                "img": self.ids.weather_img,
                "temp": self.ids.weather_H,
                "desc": self.ids.weather_desc
            },
            WeatherPanel(self.city, self.config["lang"])
        )
        self.weather_updater.start()
        if self.weather_updater._last_data is None:
            self.ids.weather_img = ''

        if self.language == languageEnum.POLISH:
            self.rss_panel = RSSUpdater("https://poranny.pl/rss/kurierporanny.xml")
        else:
            self.rss_panel = RSSUpdater("https://feeds.nbcnews.com/nbcnews/public/news")
        self.rss_updater = Updater(
            3600,
            strategy = self.rss_panel.fetch_rss
        )
        self.rss_updater.start()
        self.voice_recorder.voiceRecord(self.onRecognitionResult)

class MyApp(App):

    def build(self):
        myLayout = MyLayout()
        Clock.schedule_once(myLayout.open,0)
        return myLayout

if __name__ == "__main__":
    MyApp().run()
