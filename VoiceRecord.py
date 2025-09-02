import vosk
import pyaudio
import json
import threading
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
        else:
            info = language["start"]
        return info

    def voiceRecord(self, callback, ifTalking=False):
        self.recognized_text = ""
        self.rec_text = ""
        self.message = ""
        self.type = ""
        self.status= ""
        self.breakPoint = False
        self.COMMANDS = {
            "start": typeEnum.START,
            "stop": typeEnum.STOP,
            "end": typeEnum.END,
            "koniec": typeEnum.WEATHER,
            "weather": typeEnum.WEATHER,
            "whether": typeEnum.WEATHER,
            "pogoda": typeEnum.WEATHER
        }
        def recordAudio():
            while True:
                data = self.stream.read(1024)
                if self.rec.AcceptWaveform(data):
                    result = json.loads(self.rec.Result())
                    if ifTalking:
                        part_text = result.get('text', '').strip()
                        self.recognized_text += (' '+part_text)
                    else:
                        self.recognized_text = result.get('text', '').strip()
                    callback(self.recognized_text, typeEnum.COMMAND, False)
                    
                    for word,status in self.COMMANDS.items():
                        if word in self.recognized_text.lower():
                            self.status = status
                            self.breakPoint = True
                            break
                            
                    if self.breakPoint:
                        self.breakPoint = False
                        break
                
                            
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            
            callback(self.recognized_text, self.status, True)

        threading.Thread(target=recordAudio, daemon=True).start()