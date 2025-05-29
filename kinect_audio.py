# import pyaudio
# import wave

# # Parametry nagrywania
# FORMAT = pyaudio.paInt16       # 16-bit
# CHANNELS = 4                   # Kinect ma 4 mikrofony
# RATE = 16000                   # 16 kHz – typowe dla Kinecta
# CHUNK = 1024                   # próbki na bufor
# RECORD_SECONDS = 10
# OUTPUT_FILENAME = "kinect_audio.wav"

# # Inicjalizacja PyAudio
# p = pyaudio.PyAudio()

# # --- Lista urządzeń, aby znaleźć Kinecta ---
# print("Lista dostępnych urządzeń audio:")
# for i in range(p.get_device_count()):
#     info = p.get_device_info_by_index(i)
#     print(f"{i}: {info['name']} (Channels: {info['maxInputChannels']})")

import freenect
import numpy as np
import wave

frames = []

def audio_cb(dev, samples, timestamp):
    frames.append(np.frombuffer(samples, dtype=np.int16))

# Uruchomienie streamu audio
print("Nagrywanie z Kinecta...")
freenect.init()
freenect.start_audio(freenect.open_device(freenect.init(), 0), audio_cb)
freenect.process_events_timeout(freenect.init(), 10000)
freenect.shutdown()
print("Zakończono.")

# Zapisz do pliku WAV
samples_np = np.concatenate(frames)
wf = wave.open("kinect_audio.wav", 'wb')
wf.setnchannels(4)  # Kinect ma 4 mikrofony
wf.setsampwidth(2)  # 16 bit = 2 bajty
wf.setframerate(16000)
wf.writeframes(samples_np.tobytes())
wf.close()