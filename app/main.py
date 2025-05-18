from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from app.stt import transcribe_speech_to_text
from app.llm import generate_response
from app.tts import transcribe_text_to_speech
import os
import logging
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/voice-chat")
async def voice_chat(file: UploadFile = File(...)):
    try:
        logger.info("Menerima file audio dari frontend")
        audio_bytes = await file.read()

        logger.info("Memulai transkripsi STT")
        transcribed_text = transcribe_speech_to_text(audio_bytes, file_ext=".wav")
        logger.info(f"Hasil transkripsi: {transcribed_text}")
        if transcribed_text.startswith("[ERROR]"):
            logger.error(f"STT gagal: {transcribed_text}")
            return {"error": transcribed_text}

        logger.info("Memulai pemrosesan LLM")
        response_text = generate_response(transcribed_text)
        logger.info(f"Hasil LLM: {response_text}")
        if response_text.startswith("[ERROR]"):
            logger.error(f"LLM gagal: {response_text}")
            return {"error": response_text}

        logger.info("Memulai sintesis TTS")
        output_audio_path = transcribe_text_to_speech(response_text)
        logger.info(f"Hasil TTS: {output_audio_path}")
        if output_audio_path.startswith("[ERROR]"):
            logger.error(f"TTS gagal: {output_audio_path}")
            return {"error": output_audio_path}

        if not os.path.exists(output_audio_path):
            logger.error("File audio TTS tidak ditemukan")
            return {"error": "File audio TTS tidak ditemukan"}

        # Simpan file audio sementara untuk dikembalikan
        with open(output_audio_path, "rb") as f:
            audio_content = f.read()

        # Buat file sementara untuk respons
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_audio.write(audio_content)
        temp_audio.close()

        logger.info("Mengembalikan respons JSON")
        return {
            "audio_path": temp_audio.name,
            "transcribed_text": transcribed_text,
            "response_text": response_text
        }
    
    except Exception as e:
        logger.error(f"Error di endpoint /voice-chat: {str(e)}")
        return {"error": str(e)}

@app.get("/history")
async def get_history():
    try:
        history_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_history.json")
        if not os.path.exists(history_path):
            return {"history": []}
        
        with open(history_path, "r", encoding="utf-8") as f:
            history = f.read().strip()
        
        if not history:
            return {"history": []}
        
        import json
        history_data = json.loads(history)
        return {"history": history_data}
    except Exception as e:
        logger.error(f"Error mengambil riwayat: {str(e)}")
        return {"history": []}