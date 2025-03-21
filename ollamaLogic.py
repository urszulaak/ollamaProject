import ollama
import vosk
import pyaudio
import json

language = int(input("Choose Language (1-English, 2-Polish): "))

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

while True:
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=8192)
    if language == 1:
        print("Listening for speech. Say 'Stop' to stop. or 'End' to end")
    else:
        print("Nasluchiwanie wypowiedzi. Powiedz 'Stop' by zakończyć nagrywanie albo 'Koniec' tby zakończyć program")
    while True:
        data = stream.read(4096)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            recognized_text = result['text']
            
            print(recognized_text)

            if "stop" in recognized_text.lower():
                print("Termination keyword detected. Stopping...")
                break

            if language == 1:
                if "end" in recognized_text.lower():
                    print("Termination keyword detected. Stopping...")
                    break
            else:
                if "koniec" in recognized_text.lower():
                    print("Termination keyword detected. Stopping...")
                    end = 1
                    break  

    stream.stop_stream()
    stream.close()

    p.terminate()
    if end:
        break
    recognized_text = " ".join(recognized_text(" ", 1)[0:1])
    response = ollama.chat(
        model=model_ai,
        messages=[
            {"role": "user", "content": recognized_text},
        ],
    )
    print(response["message"]["content"])
    recognized_text = ""