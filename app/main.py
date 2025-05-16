from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from app.stt import transcribe_speech_to_text
from app.llm import generate_response
from app.tts import transcribe_text_to_speech
import os

app = FastAPI()

@app.post("/voice-chat")
async def voice_chat(file: UploadFile = File(...)):
    # Baca file audio dari frontend
    audio_bytes = await file.read()

    # Langkah 1: Transkripsi audio ke teks (STT)
    transcribed_text = transcribe_speech_to_text(audio_bytes, file_ext=".wav")
    if transcribed_text.startswith("[ERROR]"):
        return {"error": transcribed_text}

    # Langkah 2: Hasilkan respons teks menggunakan LLM
    response_text = generate_response(transcribed_text)
    if response_text.startswith("[ERROR]"):
        return {"error": response_text}

    # Langkah 3: Ubah respons teks menjadi audio (TTS)
    output_audio_path = transcribe_text_to_speech(response_text)
    if output_audio_path.startswith("[ERROR]"):
        return {"error": output_audio_path}

    # Kembalikan file audio sebagai respons
    return FileResponse(output_audio_path, media_type="audio/wav", filename="response.wav")