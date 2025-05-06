import vosk
import pyaudio
import json
import threading
from enums import typeEnum, languageEnum

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
            if language == languageEnum.ENGLISH.value:
                info = "stop - end of sentence\nexit - end chat"
            else:
                info = "stop - koniec sekwencji\nkoniec - koniec rozmowy"
        else:
            if language == languageEnum.ENGLISH.value:
                info = "start - start conversation with AI"
            else:
                info = "start - rozpocznij rozmowę z AI\npogoda - wyświetl szczegółową prognozę pogody"
        return info

    def voiceRecord(self, callback, ifTalking=False):
        self.recognized_text = ""
        self.rec_text = ""
        self.message = ""
        self.type = ""
        self.status= ""
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
                    
                    if "start" in self.recognized_text.lower():
                        self.status = typeEnum.START
                        break
                    
                    if "stop" in self.recognized_text.lower():
                        self.status = typeEnum.STOP
                        break

                    if "end" in self.recognized_text.lower() or "koniec" in self.recognized_text.lower():
                        self.status = typeEnum.END
                        break

                    if "weather" in self.recognized_text.lower() or "pogoda" in self.recognized_text.lower():
                        self.status = typeEnum.WEATHER
                        break
                
                            
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            
            callback(self.recognized_text, self.status, True)

        threading.Thread(target=recordAudio, daemon=True).start()