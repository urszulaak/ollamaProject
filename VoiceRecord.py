import vosk
import pyaudio
import json
import threading
from kivy.clock import Clock
from enums import typeEnum

class VoiceRecord():
    def __init__(self):
        self.model = None
        self.rec = None
        self.stream = None

    def voiceInitial(self, model_path, language, status=0):
        self.model = vosk.Model(model_path)
        self.rec = vosk.KaldiRecognizer(self.model, 16000)

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        frames_per_buffer=1024)
        if status == typeEnum.START.value:
            info = language["stop"]
        elif status == typeEnum.NEWS.value:
            info = language["news"]
        else:
            info = language["start"]
        return info

    def voiceRecord(self, callback, ifTalking=False):
        self.recognized_text = ""
        self.breakPoint = False
        self.COMMANDS = {
            "start": typeEnum.START,
            "stop": typeEnum.STOP,
            "end": typeEnum.END,
            "koniec": typeEnum.END,
            "weather": typeEnum.WEATHER,
            "whether": typeEnum.WEATHER,
            "pogoda": typeEnum.WEATHER,
            "wiadomości": typeEnum.NEWS,
            "news": typeEnum.NEWS,
            "rozwiń": typeEnum.EXPAND_NEWS,
            "expand": typeEnum.EXPAND_NEWS,
            "następna": typeEnum.NEXT_NEWS,
            "next": typeEnum.NEXT_NEWS,
            "wyczyść": "CLEAR_BUFFER",
            "clear": "CLEAR_BUFFER"
        }
        def recordAudio():
            buffer_text = ""
            while True:
                data = self.stream.read(1024, exception_on_overflow=False)
                if self.rec.AcceptWaveform(data):
                    result = json.loads(self.rec.Result())
                    text = result.get('text', '').strip()
                    if ifTalking:
                        self.recognized_text += (' '+text)
                        Clock.schedule_once(lambda dt: callback(self.recognized_text, typeEnum.COMMAND, False))
                    else:
                        buffer_text = text
                        Clock.schedule_once(lambda dt: callback(buffer_text, typeEnum.COMMAND, False))
                    
                else:
                    partial = json.loads(self.rec.PartialResult())
                    part_text = partial.get('partial','').strip()
                    if part_text:
                        if ifTalking:
                           Clock.schedule_once(lambda dt: callback(self.recognized_text + ' ' + part_text, typeEnum.COMMAND, False)) 
                        else:
                            buffer_text = part_text
                            Clock.schedule_once(lambda dt: callback(buffer_text, typeEnum.COMMAND, False)) 

                check_text = self.recognized_text if ifTalking else buffer_text
                for word,status in self.COMMANDS.items():
                    if word in check_text.lower():
                        if status == "CLEAR_BUFFER" and ifTalking:
                            self.recognized_text = ""
                            Clock.schedule_once(lambda dt: callback("", typeEnum.COMMAND, False))
                        else:
                            self.status = status
                            self.breakPoint = True
                        break
                        
                if self.breakPoint:
                    self.breakPoint = False
                    break
                
                            
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            
            final_text = self.recognized_text if ifTalking else buffer_text
            Clock.schedule_once(lambda dt: callback(final_text, self.status, True))

        threading.Thread(target=recordAudio, daemon=True).start()