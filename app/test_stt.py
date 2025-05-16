from stt import transcribe_speech_to_text

# Baca file audio contoh
with open("/Users/nouvalrifqi/Downloads/NewRecording.wav", "rb") as f:
    audio_bytes = f.read()

# Uji transkripsi
result = transcribe_speech_to_text(audio_bytes)
print(result)