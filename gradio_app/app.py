import os
import tempfile
import requests
import gradio as gr
import scipy.io.wavfile

# Simpan riwayat percakapan di sisi klien
chat_history = []

def voice_chat(audio):
    global chat_history
    if audio is None:
        return None, "", "", chat_history
    
    sr, audio_data = audio

    # Simpan audio sebagai file WAV sementara
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        scipy.io.wavfile.write(tmpfile.name, sr, audio_data)
        audio_path = tmpfile.name

    # Kirim ke endpoint FastAPI
    with open(audio_path, "rb") as f:
        files = {"file": ("voice.wav", f, "audio/wav")}
        response = requests.post("http://localhost:8000/voice-chat", files=files)

    # Hapus file sementara
    os.unlink(audio_path)

    if response.status_code == 200:
        response_data = response.json()
        if "error" in response_data:
            print(f"Error dari backend: {response_data['error']}")
            return None, "", "", chat_history
        
        audio_path = response_data["audio_path"]
        transcribed_text = response_data["transcribed_text"]
        response_text = response_data["response_text"]

        # Tambahkan ke riwayat
        chat_history.append([transcribed_text, response_text])
        
        return audio_path, transcribed_text, response_text, chat_history
    else:
        print(f"Error dari backend: {response.text}")
        return None, "", "", chat_history

# UI Gradio
with gr.Blocks() as demo:
    gr.Markdown("# 🎙️ Voice Chatbot")
    gr.Markdown("Berbicara langsung ke mikrofon dan dapatkan jawaban suara dari asisten AI.")

    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(sources="microphone", type="numpy", label="🎤 Rekam Pertanyaan Anda")
            transcribed_text = gr.Textbox(label="Teks Transkripsi (Input Suara)", placeholder="Transkripsi akan muncul di sini...")
            submit_btn = gr.Button("🔁 Submit")
        with gr.Column():
            audio_output = gr.Audio(type="filepath", label="🔊 Balasan dari Asisten")
            response_text = gr.Textbox(label="Teks Respons (Jawaban AI)", placeholder="Respons AI akan muncul di sini...")
    
    chat_history_display = gr.Chatbot(label="Riwayat Percakapan")

    submit_btn.click(
        fn=voice_chat,
        inputs=audio_input,
        outputs=[audio_output, transcribed_text, response_text, chat_history_display]
    )

demo.launch()