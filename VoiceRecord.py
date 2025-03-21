import vosk
import pyaudio
import json
import threading

class VoiceRecord():

    def __init__(self):
        self.model = None
        self.rec = None
        self.stream = None

    def voiceInitial(self, model_path, language):
        self.model = vosk.Model(model_path)
        self.rec = vosk.KaldiRecognizer(self.model, 16000)

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        frames_per_buffer=8192)
        if language == 1:
            info = "Listening for speech. Say 'Stop' to stop. or 'End' to end"
        else:
            info = "Nasluchiwanie wypowiedzi. Powiedz 'Stop' by zakończyć nagrywanie albo 'Koniec' by zakończyć program"
        return info
        

    def voiceRecord(self, language, callback):
        self.recognized_text = ""
        self.message = ""
        self.end = False
        def recordAudio():
            while True:
                try:
                    data = self.stream.read(4096, exception_on_overflow=False)  # Obsługa błędu przepełnienia
                except Exception as e:
                    print(f"Error reading stream: {e}")
                    break
                #data = self.stream.read(4096)
                if self.rec.AcceptWaveform(data):
                    print(f"Data length: {len(data)}")
                    print(f"First bytes: {data[:10]}")
                    result = json.loads(self.rec.Result())
                    self.recognized_text = result.get('text', '').strip()
                    
                    print(f"Recognized: {self.recognized_text}")

                    if "stop" in self.recognized_text.lower():
                        if language == 1:
                            self.message = "Termination keyword detected. Stopping..."
                        else:
                            self.message = "Wykryto słowo stopujące. Zatrzymanie..."
                            #print(self.message)
                        callback(self.recognized_text, True)
                        break

                    if language == 1:
                        if "end" in self.recognized_text.lower():
                            self.message = "Termination keyword detected. Ending..."
                            callback(self.recognized_text, True)
                            break
                    else:
                        if "koniec" in self.recognized_text.lower():
                            self.message = "Wykryto słowo kończące. Zatrzymanie..."
                            #print(self.message)
                            self.end = True
                            callback(self.recognized_text, True)
                            break  

            self.stream.stop_stream()
            self.stream.close()

            self.p.terminate()
            #print(self.message)
            self.recognized_text = " ".join(self.recognized_text(" ", 1)[0:1])
        threading.Thread(target=recordAudio, daemon=True).start()
        return self.recognized_text, self.message, self.end