from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image, AsyncImage
from VoiceRecord import VoiceRecord
from OllamaGen import OllamaGen
from enums import typeEnum, languageEnum
import os
import time
import pyttsx3
import pytdm

class BasicApp(App):

    def __init__(self, language, model_path, model_ai, **kwargs):
        super().__init__(**kwargs)
        self.language = language
        self.model_path = model_path
        self.model_ai = model_ai

    def onRecognitionResult(self, recognized_text, status, end):
        if end:
            if status == typeEnum.START:
                self.info_label.text = self.voice_recorder.voiceInitial(self.model_path, self.language, typeEnum.START.value)
                if self.language == languageEnum.ENGLISH.value:
                    self.recognized_text_label.text = "Recording..."
                else:
                    self.recognized_text_label.text = "Nagrywanie..."
                self.voice_recorder.voiceRecord(self.onRecognitionResult)
            elif status == typeEnum.STOP:
                self.recognized_text_label.text = recognized_text.rsplit(' ', 1)[0]
                self.model_generate.GenerateRespond(self.recognized_text_label.text, self.model_ai, self.onModelGenerate)
            elif status == typeEnum.END:
                self.info_label.text = self.voice_recorder.voiceInitial(self.model_path, self.language)
                self.recognized_text_label.text = ""
                self.model_answer_label.text = ""
                self.voice_recorder.voiceRecord(self.onRecognitionResult)

    def onModelGenerate(self, answer, chunk, end):
            if chunk:
                self.collect_chunk.append(chunk)
                # print(self.collect_chunk)
                # if True:
                if chunk[-1] == ".":
                    sentence = ' '.join(ch for ch in self.collect_chunk)
                    print(sentence)
                    if self.language == languageEnum.ENGLISH.value:
                    #     self.engine = pyttsx3.init()
                    #     self.engine.say(sentence)
                    #     self.engine.runAndWait()
                        os.system(f"espeak -v en-gb '{sentence}'")
                    else:
                        # pytdm.mów(sentence, "fr")
                        os.system(f"espeak -v pl '{sentence}'")
                    self.collect_chunk.clear()
            else:
                self.model_answer_label.text = answer
                if end:
                    self.i = 0
                    self.info_label.text = self.voice_recorder.voiceInitial(self.model_path, self.language, typeEnum.START.value)
                    if self.language == languageEnum.ENGLISH.value:
                        self.recognized_text_label.text = "Recording..."
                    else:
                        self.recognized_text_label.text = "Nagrywanie..."
                    self.voice_recorder.voiceRecord(self.onRecognitionResult)

    def build(self):
        layout = BoxLayout(orientation="vertical", padding=10)
        self.voice_recorder = VoiceRecord()
        self.model_generate = OllamaGen()

        self.info = self.voice_recorder.voiceInitial(self.model_path, self.language)
        self.info_label = Label(text=self.info)
        layout.add_widget(self.info_label)

        img = Image(source = 'exampleFaceStatic.png')
        layout.add_widget(img)
        # img_gif = AsyncImage(source = "faceExample.gif")
        # layout.add_widget(img_gif)

        self.voice_recorder.voiceRecord(self.onRecognitionResult)
        
        self.recognized_text_label = Label(text="")
        layout.add_widget(self.recognized_text_label)
        self.i = 0
        self.collect_chunk = []
        self.model_answer_label = Label(text="", 
                                        text_size=(300,None), 
                                        size_hint=(1, None),
                                        halign="center",
                                        valign="middle")
        self.model_answer_label.bind(size=self.model_answer_label.setter("text_size"))
        layout.add_widget(self.model_answer_label)
        
        return layout
    
    
    
# app = BasicApp()
# app.run()