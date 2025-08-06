import sounddevice as sd
import numpy as np
import whisper
import tempfile
import scipy.io.wavfile as wav
import os

#Had to add this for ffmpeg to work with whisper cuz it wasnt being detected on my  device adjust accorrdingly
os.environ["PATH"] += os.pathsep + r"C:\Users\Prateek Tripathi\Downloads\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin"

model = whisper.load_model("base")

def record_and_transcribe(duration=5, fs=16000):
    print("Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    print("Recording complete.")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav.write(f.name, fs, audio)
        print("Transcribing...")
        result = model.transcribe(f.name)
        print("You said:", result["text"])

record_and_transcribe(5)  
