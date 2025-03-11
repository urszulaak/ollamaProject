import ollama
import vosk
import pyaudio
import json

language = int(input("Choose Language (1-English, 2-Polish): "))

model_ai=""

if language == 1:
    model_path = "vosk-model-en-us-0.22-lgraph"
    model_ai = "llama3.1:8b"
elif language == 2:
    model_path = "vosk-model-small-pl-0.22"
    model_ai = "SpeakLeash/bielik-11b-v2.3-instruct:Q4_K_M"
else:
    print("Wrong language")

model = vosk.Model(model_path)
rec = vosk.KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8192)

output_file_path = "recognized_text.txt"

print("Listening for speech. Say 'Stop' to stop.")
while True:
    data = stream.read(4096)
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        recognized_text = result['text']
        
        print(recognized_text)

        if "stop" in recognized_text.lower():
            print("Termination keyword detected. Stopping...")
            break

stream.stop_stream()
stream.close()

p.terminate()

response = ollama.chat(
    model=model_ai,
    messages=[
        {"role": "user", "content": recognized_text},
    ],
)

print(response["message"]["content"])