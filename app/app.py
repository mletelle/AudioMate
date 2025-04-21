import os
import io
import json
import time
import logging
import subprocess
import mimetypes
import whisper
import streamlit as st
from datetime import datetime
from docx import Document
from docx.shared import Pt

# ========== Configuración inicial ==========
logging.basicConfig(
    filename="audiomate.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="AudioMate", layout="centered")
st.title("🎧 AudioMate - Transcribí tu audio a texto")

# ========== Subida del archivo ==========
uploaded_file = st.file_uploader(
    "📤 Elegí un archivo de audio (MP3 o WAV)",
    type=["mp3", "wav"],
    accept_multiple_files=False
)

if uploaded_file:
    try:
        # Validaciones
        filename = uploaded_file.name
        file_size = uploaded_file.size
        save_path = os.path.join(UPLOAD_DIR, filename)

        if file_size > MAX_FILE_SIZE:
            st.error(" El archivo supera los 200 MB permitidos.")
            st.stop()

        if not filename.lower().endswith((".mp3", ".wav")):
            st.error(" Solo se permiten archivos .mp3 o .wav.")
            st.stop()

        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type not in ["audio/mpeg", "audio/wav"]:
            st.error(" Tipo de archivo no permitido.")
            st.stop()

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(" Archivo subido y guardado correctamente.")
        logging.info(f"Archivo recibido: {filename}")

        # ========== Conversión con FFmpeg ==========
        output_path = os.path.join(UPLOAD_DIR, f"converted_{filename.rsplit('.', 1)[0]}.wav")
        ffmpeg_cmd = [
            "ffmpeg", "-i", save_path,
            "-ar", "16000", "-ac", "1", output_path
        ]

        with st.spinner("🎧 Convirtiendo a WAV mono 16 kHz..."):
            subprocess.run(ffmpeg_cmd, check=True)

        st.success(f"🎵 Conversión completada: {output_path}")
        logging.info(f"Archivo convertido: {output_path}")

        # ========== Validación con ffprobe ==========
        def verificar_audio(path):
            """Devuelve metadatos de un archivo de audio usando ffprobe."""
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-show_streams", "-print_format", "json", path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return json.loads(result.stdout)

        info = verificar_audio(output_path)
        st.write(f" Duración: {float(info['format']['duration']):.2f}s | 🎚 Canales: {info['streams'][0]['channels']} | 🎼 Sample Rate: {info['streams'][0]['sample_rate']} Hz")

        # ========== Transcripción con Whisper ==========
        model = whisper.load_model("base")  # podés cambiar a "small", "medium", etc.

        with st.spinner(" Transcribiendo..."):
            result = model.transcribe(output_path)

        st.success(" Transcripción completada.")
        transcripcion = result["text"]
        segments = result["segments"]

        if not segments:
            st.warning("⚠️ No se detectó habla clara en el audio.")
            st.stop()

        st.subheader(" Transcripción:")
        st.text_area("Texto generado", transcripcion, height=300)

        for seg in segments:
            st.write(f"[{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['text']}")

        # ========== Descarga de archivos ==========
        fecha = datetime.now().strftime("%Y-%m-%d")
        nombre_base = filename.rsplit('.', 1)[0]

        # TXT
        txt_buffer = io.StringIO()
        txt_buffer.write(f"Archivo original: {filename}\nFecha: {fecha}\n\n{transcripcion}")
        txt_buffer.seek(0)
        st.download_button("📄 Descargar como TXT", txt_buffer, f"transcripcion_{fecha}_{nombre_base}.txt", mime="text/plain")

        # DOCX
        doc = Document()
        doc.add_heading("Transcripción de audio", 0)
        doc.add_paragraph(f"Archivo original: {filename}")
        doc.add_paragraph(f"Fecha: {fecha}")
        doc.add_paragraph("")
        for segmento in segments:
            doc.add_paragraph(f"[{segmento['start']:.2f}s - {segmento['end']:.2f}s] {segmento['text']}", style='List Bullet')
        docx_buffer = io.BytesIO()
        doc.save(docx_buffer)
        docx_buffer.seek(0)
        st.download_button(" Descargar como DOCX", docx_buffer, f"transcripcion_{fecha}_{nombre_base}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        # ========== Registro JSON de actividad ==========
        registro_path = os.path.join(UPLOAD_DIR, "procesados.json")
        registro = []

        if os.path.exists(registro_path):
            with open(registro_path, "r") as f:
                registro = json.load(f)

        registro.append({
            "filename": filename,
            "converted": output_path,
            "fecha": datetime.now().isoformat(),
            "transcripcion": transcripcion[:100] + "..." if len(transcripcion) > 100 else transcripcion
        })

        with open(registro_path, "w") as f:
            json.dump(registro, f, indent=2)

        # ========== Limpieza ==========
        try:
            os.remove(save_path)
            os.remove(output_path)
            st.info(" Archivos temporales eliminados.")
        except Exception as e:
            st.warning(f"No se pudieron eliminar los archivos temporales: {e}")

    except Exception as e:
        st.error(f" Error inesperado: {e}")
        logging.error(f"Error crítico: {e}")
        st.stop()
