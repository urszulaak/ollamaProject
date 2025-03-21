from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from VoiceRecord import VoiceRecord

class BasicApp(App):

    def __init__(self, language, model_path, model_ai, **kwargs):
        super().__init__(**kwargs)
        self.language = language
        self.model_path = model_path
        self.model_ai = model_ai

    def onRecognitionResult(self, recognized_text, end):
        if end:
            print("wynik" + recognized_text)
            self.recognized_text = recognized_text

    def build(self):
        layout = GridLayout(cols=1)
        img = Image(source = 'exampleFaceStatic.png')
        self.voice_recorder = VoiceRecord()

        self.info = self.voice_recorder.voiceInitial(self.model_path, self.language)
        layout.add_widget(Label(text=self.info))

        layout.add_widget(img)
        self.voice_recorder.voiceRecord(self.language, self.onRecognitionResult)
        self.recognized_text_label = Label(text="Waiting for speech...")
        layout.add_widget(self.recognized_text_label)
        return layout
    
    
    
# app = BasicApp()
# app.run()