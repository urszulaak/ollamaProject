import wave
import pyaudio

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)

frames = []
for _ in range(100):  # 100 próbek (~2 sekundy)
    data = stream.read(4096)
    frames.append(data)

stream.stop_stream()
stream.close()
p.terminate()

with wave.open("test.wav", "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b''.join(frames))

print("Plik test.wav zapisany. Otwórz go i sprawdź dźwięk.")
