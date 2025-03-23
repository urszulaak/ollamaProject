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
                info = "stop - end of sentence, exit - end chat"
            else:
                info = "stop - koniec sekwencji, koniec - koniec rozmowy"
        else:
            if language == languageEnum.ENGLISH.value:
                info = "start - start conversation with AI"
            else:
                info = "start - rozpocznij rozmowę z AI"
        return info

    def voiceRecord(self, callback):
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
                    self.recognized_text = result.get('text', '').strip()
                    print(self.recognized_text)
                    
                    if "start" in self.recognized_text.lower():
                        self.status = typeEnum.START
                        break
                    
                    if "stop" in self.recognized_text.lower():
                        self.status = typeEnum.STOP
                        break

                    if "end" in self.recognized_text.lower() or "koniec" in self.recognized_text.lower():
                        self.status = typeEnum.END
                
                            
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()

            match self.status:
                case typeEnum.START:
                    callback(self.recognized_text, typeEnum.START, True)
                case typeEnum.STOP:
                    callback(self.recognized_text, typeEnum.STOP, True)
                case typeEnum.END:
                    callback(self.recognized_text, typeEnum.END, True)
                case default:
                    pass   
        threading.Thread(target=recordAudio, daemon=True).start()