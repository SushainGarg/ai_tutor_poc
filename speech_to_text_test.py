import os
import whisper

def stt_whisper(audio_file):
    try:
        print('Loading whisper model')
        model = whisper.load_model("base")
        
        print('transcription generation: ....')
        result = model.transcribe(audio_file)
        
        print("\n -------- transcription -------------")
        print(result['text'])
        print("--------------------------------------\n")
    except Exception as e:
        print(f"error occured : {e}")
        
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    audio_file =  "C:/Users/sgarg10/harvard.wav"
    print(audio_file)
    stt_whisper(audio_file)