import ollama
import vosk
import pyaudio
import json

model_path = ""

language = int(input("Choose Language (1-English, 2-Polish): "))

if language == 1:
    model_path = "vosk-model-en-us-0.22-lgraph"
elif language == 2:
    model_path = "vosk-model-small-pl-0.22"
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

with open(output_file_path, "w") as output_file:
    print("Listening for speech. Say 'Amen' to stop.")
    while True:
        data = stream.read(4096)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            recognized_text = result['text']
            
            output_file.write(recognized_text + "\n")
            print(recognized_text)

            if "amen" in recognized_text.lower():
                print("Termination keyword detected. Stopping...")
                break

stream.stop_stream()
stream.close()

p.terminate()

#content = input("Enter message: ")

response = ollama.chat(
    model="llama3.1:8b",
    messages=[
        {"role": "user", "content": recognized_text},
    ],
)

print(response["message"]["content"])