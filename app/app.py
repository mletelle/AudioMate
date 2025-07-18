import os
import io
import json
import logging
import subprocess
import streamlit as st
from datetime import datetime
from docx import Document

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

uploaded_file = st.file_uploader(
    "Elegí un archivo de audio (MP3, WAV o M4A) – Límite: hasta 1000 MB",
    type=["mp3", "wav", "m4a"],
    accept_multiple_files=False
)

if uploaded_file:
    try:
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

        output_path = os.path.join(
            UPLOAD_DIR,
            f"processed_{filename.rsplit('.', 1)[0]}.wav"
        )

        filter_chain = (
            "afftdn=nr=15:om=0.9,"
            "highpass=f=100,"
            "lowpass=f=8000,"
            "equalizer=f=300:width_type=q:width=200:g=-4,"
            "equalizer=f=3000:width_type=q:width=1000:g=3,"
            "equalizer=f=6000:width_type=q:width=200:g=-3,"
            "acompressor=threshold=-20dB:ratio=4:attack=5:release=200:makeup=6,"
            "loudnorm=I=-16:TP=-1:LRA=7:print_format=summary"
        )

        ffmpeg_cmd = [
            "ffmpeg",
            "-y",                   
            "-i", save_path,
            "-af", filter_chain,
            "-ar", "16000",
            "-ac", "1",
            output_path
        ]

        with st.spinner(" Procesando audio (ruido → EQ → compresión → normalización)…"):
            subprocess.run(ffmpeg_cmd, check=True)

        st.success(f" Audio procesado: {output_path}")
        logging.info(f"ffmpeg cmd: {' '.join(ffmpeg_cmd)}")


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

        device = "cpu" if os.getenv("WHISPER_FORCE_CPU") == "1" else "cuda"
        model_name = os.getenv("WHISPER_MODEL", "large-v2")
        compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "float16")
        from faster_whisper import WhisperModel
        model = WhisperModel(
            model_name,
            device=device,
            compute_type=compute_type,
            download_root=os.environ.get("WHISPER_CACHE", ".cache/whisper")
        )


        logging.info(f"Whisper model loaded: {model_name} on {device}")


        with st.spinner(" Transcribiendo..."):
            try:
                result = model.transcribe(output_path, language="es")
            except RuntimeError as e:
                if "device-side assert triggered" in str(e):
                    st.warning(" Falla en GPU, reintentando en CPU…")
                    model_cpu = WhisperModel("small",
                                            device="cpu",
                                            compute_type="int8")
                    result = model_cpu.transcribe(output_path,
                                                language="es")

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


        #  DOCX
        doc = Document()
        doc.add_heading("Transcripción de audio", level=0)
        doc.add_paragraph(f"Archivo original: {filename}")
        doc.add_paragraph(f"Fecha: {fecha}")
        doc.add_paragraph("")  # salto de línea
        doc.add_heading("Texto completo", level=1)
        doc.add_paragraph(transcripcion)
        docx_buffer = io.BytesIO()
        doc.save(docx_buffer)
        docx_buffer.seek(0)
        st.download_button(
            "Descargar como DOCX",
            docx_buffer,
            file_name=f"transcripcion_{fecha}_{nombre_base}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

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
