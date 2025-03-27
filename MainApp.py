from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from VoiceRecord import VoiceRecord
from OllamaGen import OllamaGen
from enums import typeEnum, languageEnum
import os

class MyLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.language = 2
        self.model_path = "vosk-model-small-pl-0.22"
        self.model_ai = "SpeakLeash/bielik-11b-v2.3-instruct:Q4_K_M"
        self.collect_chunk = []
        self.voice_recorder = VoiceRecord()
        self.model_generate = OllamaGen()

    def onRecognitionResult(self, recognized_text, status, end):
        if end:
            if status == typeEnum.START:
                # self.ids.face_img.opacity = 1
                self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.language, typeEnum.START.value)
                if self.language == languageEnum.ENGLISH.value:
                    self.ids.command.text = "Recording..."
                else:
                    self.ids.command.text = "Nagrywanie..."
                self.voice_recorder.voiceRecord(self.onRecognitionResult)
            elif status == typeEnum.STOP:
                self.ids.command.text = recognized_text.rsplit(' ', 1)[0]
                self.model_generate.GenerateRespond(self.ids.command.text, self.language, self.onModelGenerate)
            elif status == typeEnum.END:
                self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.language)
                self.ids.command.text = ""
                self.ids.model_response.text = ""
                # self.ids.face_img.opacity = 0
                self.voice_recorder.voiceRecord(self.onRecognitionResult)
        else:
            self.ids.command.text = recognized_text

    def onModelGenerate(self, answer, chunk, end):
            if chunk:
                self.collect_chunk.append(chunk)
                if chunk[-1] == "." or chunk[-1] == "!" or chunk[-1] == "?":
                    sentence = ' '.join(ch for ch in self.collect_chunk)
                    if self.language == languageEnum.ENGLISH.value:
                        os.system(f"espeak -v en-gb '{sentence}'")
                    else:
                        os.system(f"espeak -v pl '{sentence}'")
                    self.collect_chunk.clear()
            else:
                self.ids.model_response.text = answer
                if end:
                    if self.collect_chunk:
                        sentence = ' '.join(self.collect_chunk)
                        if self.language == languageEnum.ENGLISH.value:
                            os.system(f"espeak -v en-gb '{sentence}'")
                        else:
                            os.system(f"espeak -v pl '{sentence}'")
                        self.collect_chunk.clear()
                    self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.language, typeEnum.START.value)
                    if self.language == languageEnum.ENGLISH.value:
                        self.ids.command.text = "Recording..."
                    else:
                        self.ids.command.text = "Nagrywanie..."
                    self.voice_recorder.voiceRecord(self.onRecognitionResult)
    
    def wlacz(self, dt):
        self.info = self.voice_recorder.voiceInitial(self.model_path, self.language)
        self.ids.header.text = self.info
        # self.ids.face_img.opacity = 0
        self.voice_recorder.voiceRecord(self.onRecognitionResult)

class MyApp(App):

    def build(self):
        myLayout = MyLayout()
        Clock.schedule_once(myLayout.wlacz,0)
        return myLayout

if __name__ == "__main__":
    MyApp().run()
