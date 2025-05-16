import os
import uuid
import tempfile
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# path ke folder utilitas TTS
COQUI_DIR = os.path.join(BASE_DIR, "coqui_utils")

# TODO: Lengkapi jalur path ke file model TTS
# File model (misalnya checkpoint_1260000-inference.pth) harus berada di dalam folder coqui_utils/
COQUI_MODEL_PATH = os.path.join(COQUI_DIR, "checkpoint_1260000-inference.pth")

# TODO: Lengkapi jalur path ke file konfigurasi
# File config.json harus berada di dalam folder coqui_utils/
COQUI_CONFIG_PATH = os.path.join(COQUI_DIR, "config.json")

# TODO: Tentukan nama speaker yang digunakan
# Pilih nama speaker yang sesuai dengan isi file speakers.pth (misalnya: "wibowo")
COQUI_SPEAKER = COQUI_SPEAKER = "wibowo"

def transcribe_text_to_speech(text: str) -> str | None:
    return _tts_with_coqui(text)

# === ENGINE 1: Coqui TTS ===
def _tts_with_coqui(text: str) -> str | None:
    tmp_dir = tempfile.gettempdir()
    output_path = os.path.join(tmp_dir, f"tts_{uuid.uuid4()}.wav")

    cmd = [
    "tts",
    "--text", text,
    "--model_path", COQUI_MODEL_PATH,  # Gunakan path absolut
    "--config_path", COQUI_CONFIG_PATH,  # Gunakan path absolut
    "--speaker_idx", COQUI_SPEAKER,
    "--out_path", output_path
]
    
    try:
        subprocess.run(cmd, check=True, cwd=COQUI_DIR)
        return output_path  # hanya return jika sukses
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] TTS subprocess failed: {e}")
        return None

