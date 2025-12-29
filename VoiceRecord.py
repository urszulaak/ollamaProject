import vosk
import pyaudio
import json
import threading
from kivy.clock import Clock
from enums import typeEnum

class VoiceRecord():
    def __init__(self):
        self.model = None
        self.stream = None
        self.COMMANDS = {}
        self.aiCOMMANDS = {}
        self.is_recording = False 

    def voiceInitial(self, model_path, language, status=0):
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
                
        self.model = vosk.Model(model_path)
        self.COMMANDS = language.get("commands", {})
        self.aiCOMMANDS = language.get("aiCommands", {})
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=16000,
                                input=True,
                                frames_per_buffer=1024)
        
        infos = language.get("info", {})
        if status == typeEnum.START.value:
            info = infos.get("stop", "")
        elif status == typeEnum.NEWS.value:
            info = infos.get("news", "")
        else:
            info = infos.get("start", "")
        return info

    def voiceRecord(self, callback, ifTalking=False):
        self.recognized_text = ""
        self.status = ""
        self.breakPoint = False
        self.is_recording = True

        if ifTalking:
            rec = vosk.KaldiRecognizer(self.model, 16000)
        else:
            grammar_list = list(self.COMMANDS.keys()) + ["[unk]"]
            grammar_json = json.dumps(grammar_list, ensure_ascii=False)
            rec = vosk.KaldiRecognizer(self.model, 16000, grammar_json)

        def recordAudio():
            while self.is_recording:
                try:
                    data = self.stream.read(1024, exception_on_overflow=False)
                except OSError:
                    break

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text_result = result.get('text', '').strip()
                    
                    if text_result == "[unk]":
                        text_result = ""

                    if ifTalking:
                        if text_result:
                            self.recognized_text += (' ' + text_result)
                            Clock.schedule_once(lambda dt: callback(self.recognized_text.strip(), typeEnum.COMMAND, False))

                        current_text_lower = self.recognized_text.lower()
                        for word, status in self.aiCOMMANDS.items():
                            if word in text_result.lower(): 
                                if status == "CLEAR_BUFFER":
                                    self.recognized_text = ""
                                    Clock.schedule_once(lambda dt: callback("", typeEnum.COMMAND, False))
                                else:
                                    self.status = status
                                    self.breakPoint = True
                                break
                    
                    else:
                        if text_result:
                            self.recognized_text = text_result
                            Clock.schedule_once(lambda dt: callback(self.recognized_text, typeEnum.COMMAND, False))

                            if text_result in self.COMMANDS:
                                self.status = self.COMMANDS[text_result]
                                self.breakPoint = True
                    
                    if self.breakPoint:
                        self.is_recording = False
                        break
            
            try:
                self.stream.stop_stream()
                self.stream.close()
                self.p.terminate()
            except:
                pass
            
            Clock.schedule_once(lambda dt: callback(self.recognized_text.strip(), self.status, True))

        threading.Thread(target=recordAudio, daemon=True).start()
