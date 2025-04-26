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


# ========== Configuración inicial ==========
logging.basicConfig(
    filename="audiomate.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 1000 * 1024 * 1024  # 1000 MB
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="AudioMate", layout="centered")
st.title(" AudioMate - Transcribí tu audio a texto")

# ========== Subida del archivo ==========
uploaded_file = st.file_uploader(
    " Elegí un archivo de audio (MP3, WAV o M4A)",
    type=["mp3", "wav", "m4a"],
    accept_multiple_files=False
)

if uploaded_file:
    try:
        # Validaciones
        filename = uploaded_file.name
        file_size = uploaded_file.size
        save_path = os.path.join(UPLOAD_DIR, filename)

        if file_size > MAX_FILE_SIZE:
            st.error(" El archivo supera los 1000 MB permitidos.")
            st.stop()

        if not filename.lower().endswith((".mp3", ".wav", ".m4a")):
            st.error(" Solo se permiten archivos .mp3, .m4a o .wav.")
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
        st.write(f" Duración: {float(info['format']['duration']):.2f}s | Canales: {info['streams'][0]['channels']} |  Sample Rate: {info['streams'][0]['sample_rate']} Hz")

        # ========== Transcripción con Whisper ==========

        device = "cpu" if os.getenv("WHISPER_FORCE_CPU") == "1" else "cuda"
        model = whisper.load_model("base", device=device) # podés cambiar a "small", "medium", etc.

        with st.spinner(" Transcribiendo..."):
            try:
                result = model.transcribe(output_path)
            except RuntimeError as e:
                if "device-side assert triggered" in str(e):
                    st.warning(" Falla en GPU, reintentando en CPU…")
                    model_cpu = whisper.load_model("base", device="cpu")
                    result = model_cpu.transcribe(output_path)
                else:
                    raise

        st.success(" Transcripción completada.")
        transcripcion = result["text"]
        segments = result["segments"]

        if not segments:
            st.warning(" No se detectó habla clara en el audio.")
            st.stop()

        st.subheader(" Transcripción:")
        st.text_area("Texto generado", transcripcion, height=300)

        with st.expander("Ver detalle de segmentos", expanded=False):
            seg_text = "\n".join(
                f"[{seg['start']:.2f}s – {seg['end']:.2f}s] {seg['text']}"
                for seg in segments
            )
            st.text_area(
                "Segmentos",
                value=seg_text,
                height=200
            )

        # ========== Descarga de archivos ==========
        fecha = datetime.now().strftime("%Y-%m-%d")
        nombre_base = filename.rsplit('.', 1)[0]

        # TXT
        txt_buffer = io.BytesIO()
        if hasattr(transcripcion, "getvalue"):
            transcripcion = transcripcion.getvalue()
        contenido_txt = f"Archivo original: {filename}\nFecha: {fecha}\n\n{transcripcion}"
        txt_buffer.write(contenido_txt.encode("utf-8"))
        txt_buffer.seek(0)
        txt_buffer.name = "dummy.txt"  
        st.download_button(
            "Descargar como TXT",
            txt_buffer,
            f"transcripcion_{fecha}_{nombre_base}.txt",
            mime="text/plain"
        )


        # ========== DOCX ==========
        doc = Document()
        doc.add_heading("Transcripción de audio", level=0)
        doc.add_paragraph(f"Archivo original: {filename}")
        doc.add_paragraph(f"Fecha: {fecha}")
        doc.add_paragraph("")  # salto de línea
        doc.add_heading("Texto completo", level=1)
        doc.add_paragraph(transcripcion)
        doc.add_heading("Segmentos", level=1)
        for seg in segments:
            doc.add_paragraph(
                f"[{seg['start']:.2f}s – {seg['end']:.2f}s] {seg['text']}",
                style="List Bullet"
            )
        docx_buffer = io.BytesIO()
        doc.save(docx_buffer)
        docx_buffer.seek(0)
        st.download_button(
            "Descargar como DOCX",
            docx_buffer,
            file_name=f"transcripcion_{fecha}_{nombre_base}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        # ========== Registro JSON de actividad ==========
        registro_path = os.path.join(UPLOAD_DIR, "procesados.json")
        registro = []
        if os.path.exists(registro_path):
            try:
                with open(registro_path) as f:
                    registro = json.load(f)
            except (ValueError, json.JSONDecodeError):
                registro = []

        registro.append({
            "filename": filename,
            "converted": output_path,
            "fecha": datetime.now().isoformat(),
            "transcripcion": transcripcion[:100] + "..." if len(transcripcion) > 100 else transcripcion
        })

        with open(registro_path, "w", encoding="utf-8") as f:
            json.dump(registro, f, ensure_ascii=False, indent=2)

        # ========== Limpieza ==========
        removed = 0
        for f in os.listdir(UPLOAD_DIR):
            if f.lower().endswith((".mp3", ".wav", ".m4a")):
                fp = os.path.join(UPLOAD_DIR, f)
                try:
                    os.remove(fp)
                    removed += 1
                except Exception as e:
                    logging.warning(f"No se pudo eliminar {fp}: {e}")
        st.info(f"Se eliminaron {removed} archivos de audio temporales.")

    except Exception as e:
        st.error(f" Error inesperado: {e}")
        logging.error(f"Error crítico: {e}")
        st.stop()
