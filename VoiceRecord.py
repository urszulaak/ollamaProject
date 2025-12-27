import vosk
import pyaudio
import json
import threading
from enums import typeEnum

class VoiceRecord():
    def __init__(self):
        self.model = None
        self.stream = None
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
            "poprzednia": typeEnum.PREVIOUS_NEWS,
            "previous": typeEnum.PREVIOUS_NEWS
        }
        self.aiCOMMANDS = {
            "start": typeEnum.START,
            "stop": typeEnum.STOP,
            "exit": typeEnum.END,
            "koniec": typeEnum.END,
            "wyczyść": "CLEAR_BUFFER",
            "clear": "CLEAR_BUFFER"
        }

    def voiceInitial(self, model_path, language, status=0):
        self.model = vosk.Model(model_path)

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
        self.status = ""
        self.breakPoint = False

        if ifTalking:
            rec = vosk.KaldiRecognizer(self.model, 16000)
        else:
            grammar_list = list(self.COMMANDS.keys()) + ["[unk]"]
            grammar_json = json.dumps(grammar_list)

            rec = vosk.KaldiRecognizer(self.model, 16000, grammar_json)

        def recordAudio():
            while True:
                data = self.stream.read(1024, exception_on_overflow=False)
                
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text_result = result.get('text', '').strip()
                    
                    if text_result == "[unk]":
                        text_result = ""

                    if ifTalking:
                        if text_result:
                            self.recognized_text += (' ' + text_result)
                            callback(self.recognized_text.strip(), typeEnum.COMMAND, False)

                        current_text_lower = self.recognized_text.lower()
                        
                        for word, status in self.aiCOMMANDS.items():
                            if word in text_result.lower(): 
                                if status == "CLEAR_BUFFER":
                                    self.recognized_text = ""
                                    callback("", typeEnum.COMMAND, False)
                                else:
                                    self.status = status
                                    self.breakPoint = True
                                break
                    
                    else:
                        if text_result:
                            self.recognized_text = text_result
                            callback(self.recognized_text, typeEnum.COMMAND, False)

                            if text_result in self.COMMANDS:
                                self.status = self.COMMANDS[text_result]
                                self.breakPoint = True
                    
                    if self.breakPoint:
                        self.breakPoint = False
                        break
            
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            
            callback(self.recognized_text.strip(), self.status, True)

        threading.Thread(target=recordAudio, daemon=True).start()

```
