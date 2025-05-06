from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.text import LabelBase
from VoiceRecord import VoiceRecord
from OllamaGen import OllamaGen
from WeatherPanel import WeatherPanel
from enums import typeEnum, languageEnum
import os
LabelBase.register(name="EmojiFont", fn_regular="NotoColorEmoji.ttf")

class MyLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.language = languageEnum.POLISH
        self.model_path = "vosk-model-small-pl-0.22"
        self.model_ai = "SpeakLeash/bielik-11b-v2.3-instruct:Q4_K_M"
        self.collect_chunk = []
        self.voice_recorder = VoiceRecord()
        self.model_generate = OllamaGen()
        self.img_animation_event = None
        self.img_animation_index = 0
        self.img_animation_sources = ["mask_O.png", "mask_half_smile.png", "mask_full_smile.png"]
        self.punctuation = ["i", "a", "ale", "lecz", "lub", "czy", "więc", "zatem", "natomiast","że", "ponieważ", "gdy", "kiedy", "jeśli", "chociaż", "aby", "który", "która", "które"]
        self.punctuation_mark = [".", "!", "?", ","]

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
                self.ids.columns.size_hint_y = 0.0
                self.ids.model_response.size_hint_y = 0.8
                self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.language, typeEnum.START.value)
                if self.language == languageEnum.ENGLISH:
                    self.ids.command.text = "Recording..."
                else:
                    self.ids.command.text = "Nagrywanie..."
                self.voice_recorder.voiceRecord(self.onRecognitionResult, True)
            elif status == typeEnum.STOP:
                self.ids.command.text = recognized_text.rsplit(' ', 1)[0]
                Clock.schedule_once(lambda dt: self.change_img("mask_think.png"))
                self.model_generate.GenerateRespond(self.ids.command.text, self.language, self.onModelGenerate)
            elif status == typeEnum.END:
                self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.language)
                self.ids.command.text = ""
                self.ids.model_response.text = ""
                self.voice_recorder.voiceRecord(self.onRecognitionResult)
            elif status == typeEnum.WEATHER:
                self.ids.model_response.size_hint_y = 0.1
                self.ids.columns.size_hint_y = 0.7
                self.ids.model_response.text = str(self.weather[0])
                columns = [
                    ('col1', 1, 2, 3, 4, 5),
                    ('col2', 6, 7, 8, 9, 10),
                    ('col3', 11, 12, 13, 14, 15)
                ]
                for col_id, day_idx, img_idx, desc_idx, high_idx, low_idx in columns:
                    self.ids[f'{col_id}_img'].text = str(self.weather[img_idx])
                    self.ids[f'{col_id}_day'].text = str(self.weather[day_idx])
                    self.ids[f'{col_id}_desc'].text = str(self.weather[desc_idx])
                    self.ids[f'{col_id}_H'].text = str(self.weather[high_idx])
                    self.ids[f'{col_id}_L'].text = str(self.weather[low_idx])
                self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.language)
                self.voice_recorder.voiceRecord(self.onRecognitionResult)
        else:
            self.ids.command.text = recognized_text

    def onModelGenerate(self, answer, chunk, end):
            if chunk:
                self.collect_chunk.append(chunk)
                if chunk in self.punctuation or chunk[-1] in self.punctuation_mark:
                    if chunk in self.punctuation:
                        self.collect_chunk.pop()
                    sentence = ' '.join(ch for ch in self.collect_chunk)
                    self.start_img_animation()
                    if self.language == languageEnum.ENGLISH.value:
                        os.system(f"espeak -v en-gb '{sentence}'")
                    else:
                        os.system(f"espeak -v pl '{sentence}'")
                    self.stop_img_animation()
                    self.collect_chunk.clear()
                    if chunk in self.punctuation:
                        self.collect_chunk.append(chunk)
            else:
                self.ids.model_response.text = answer
                if end:
                    if self.collect_chunk:
                        sentence = ' '.join(self.collect_chunk)
                        self.start_img_animation()
                        if self.language == languageEnum.ENGLISH.value:
                            os.system(f"espeak -v en-gb '{sentence}'")
                        else:
                            os.system(f"espeak -v pl '{sentence}'")
                        self.stop_img_animation()
                    self.onRecognitionResult("", typeEnum.START, True)
    
    def wlacz(self, dt):
        self.info = self.voice_recorder.voiceInitial(self.model_path, self.language)
        self.ids.header.text = self.info
        weather_panel = WeatherPanel("Bialystok", languageEnum.POLISH)
        self.weather = weather_panel.fetch_weather()
        self.voice_recorder.voiceRecord(self.onRecognitionResult)

class MyApp(App):

    def build(self):
        myLayout = MyLayout()
        Clock.schedule_once(myLayout.wlacz,0)
        return myLayout

if __name__ == "__main__":
    MyApp().run()
