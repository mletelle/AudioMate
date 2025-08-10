#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AudioMate – Transcripción de audio a texto
-----------------------------------------
• Procesa uno o varios archivos MP3/WAV/M4A (≤ 1000 MB c/u)
• Muestra progreso en tiempo real
• Usa GPU si está disponible (o CPU forzada con WHISPER_FORCE_CPU=1)
• Descarga individual (TXT / DOCX) y ZIP global
"""

import io
import json
import re
import logging
import os
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import streamlit as st
import torch
from docx import Document
from faster_whisper import WhisperModel

# ───────────────────────────── Configuración general ──────────────────────────

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 1_000 * 1024 * 1024  # 1000 MB
os.makedirs(UPLOAD_DIR, exist_ok=True)

logging.basicConfig(
    filename="audiomate.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

st.set_page_config(page_title="AudioMate", layout="centered")
st.title("🎧 AudioMate – Transcribí tu audio a texto")

# ────────────────────────────── Dispositivo y modelo ──────────────────────────

DEVICE = (
    "cpu"
    if os.getenv("WHISPER_FORCE_CPU") == "1"
    else ("cuda" if torch.cuda.is_available() else "cpu")
)
st.sidebar.success(f"Dispositivo en uso: **{'GPU' if DEVICE == 'cuda' else 'CPU'}**")

MODEL = WhisperModel(
    os.getenv("WHISPER_MODEL", "large-v2"),
    device=DEVICE,
    compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "float16"),
    download_root=os.getenv("WHISPER_CACHE", ".cache/whisper"),
)
logging.info("Whisper model cargado correctamente")

# ──────────────────────────────── Utilidades ──────────────────────────────────


def _guardar_archivo(uploaded_file, destino: Path) -> None:
    """Guarda el archivo subido en disco."""
    with destino.open("wb") as f:
        f.write(uploaded_file.getbuffer())


def _ffprobe(path: Path) -> Dict[str, Any]:
    """Devuelve metadatos de audio vía ffprobe (JSON)."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-show_streams",
        "-print_format",
        "json",
        str(path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(res.stdout)


def _segment_text(seg) -> str:
    return seg.text if hasattr(seg, "text") else seg["text"]

def _dedupe(text: str, max_rep: int = 3) -> str:
    """
    Colapsa repeticiones consecutivas de la misma palabra
    (ej. «probando probando probando…») dejando como máximo `max_rep`.
    Muy útil para los casos en que Whisper alarga la salida.
    """
    out, cnt, prev = [], 0, None
    for tok in text.split():
        base = tok.lower()
        if base == prev:
            cnt += 1
            if cnt <= max_rep:
                out.append(tok)
        else:
            prev, cnt = base, 1
            out.append(tok)
    return re.sub(r'\s+', ' ', " ".join(out)).strip()

def _segment_val(seg, attr):
    if hasattr(seg, attr):
        return getattr(seg, attr)
    if isinstance(seg, dict):
        return seg[attr]
    raise AttributeError(attr)


def _export_txt(file_name: str, fecha: str, texto: str) -> bytes:
    buf = io.BytesIO()
    buf.write(f"Archivo original: {file_name}\nFecha: {fecha}\n\n{texto}".encode("utf-8"))
    buf.seek(0)
    return buf.getvalue()


def _export_docx(file_name: str, fecha: str, texto: str) -> bytes:
    doc = Document()
    doc.add_heading("Transcripción de audio", level=0)
    doc.add_paragraph(f"Archivo original: {file_name}")
    doc.add_paragraph(f"Fecha: {fecha}")
    doc.add_paragraph("")
    doc.add_heading("Texto completo", level=1)
    doc.add_paragraph(texto)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


def _filter_chain() -> str:
    """Cadena de filtros ffmpeg fija."""
    return (
        "afftdn=nr=15:om=0.9,"
        "highpass=f=100,"
        "lowpass=f=8000,"
        "equalizer=f=300:width_type=q:width=200:g=-4,"
        "equalizer=f=3000:width_type=q:width=1000:g=3,"
        "equalizer=f=6000:width_type=q:width=200:g=-3,"
        "acompressor=threshold=-20dB:ratio=4:attack=5:release=200:makeup=6,"
        "loudnorm=I=-16:TP=-1:LRA=7:print_format=summary"
    )


def _preprocesar_audio(entrada: Path, salida: Path) -> None:
    """Normaliza y convierte el audio a WAV 16 kHz / mono."""
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(entrada),
        "-af",
        _filter_chain(),
        "-ar",
        "16000",
        "-ac",
        "1",
        str(salida),
    ]
    subprocess.run(cmd, check=True)
    logging.info("ffmpeg cmd: %s", " ".join(cmd))



files = st.file_uploader(
    "Elegí **uno o varios** archivos de audio (MP3, WAV o M4A) – Límite: 1000 MB c/u",
    type=["mp3", "wav", "m4a"],
    accept_multiple_files=True,
)

if files:
    try:
        zip_outputs: List[Dict[str, bytes]] = []
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")

        for idx, upl in enumerate(files, 1):
            st.header(f"📄 {idx}. {upl.name}")

            if upl.size > MAX_FILE_SIZE:
                st.error(" Supera los 1000 MB permitidos; se omite.")
                continue
            if not upl.name.lower().endswith(("mp3", "wav", "m4a")):
                st.error(" Formato no soportado; se omite.")
                continue

            src_path = Path(UPLOAD_DIR) / upl.name
            _guardar_archivo(upl, src_path)
            st.success(" Archivo guardado correctamente")

            wav_path = src_path.with_name(f"processed_{src_path.stem}.wav")

            with st.spinner(" Procesando audio (ruido → EQ → compresión → normalización)…"):
                _preprocesar_audio(src_path, wav_path)

            meta = _ffprobe(wav_path)
            dur = float(meta["format"]["duration"])
            canales = meta["streams"][0]["channels"]
            sr = meta["streams"][0]["sample_rate"]
            st.info(f" Duración: {dur:.2f}s  |  Canales: {canales}  |  SR: {sr} Hz")

            progress = st.progress(0.0, text=" Transcribiendo…")
            try:
                segments_gen, _ = MODEL.transcribe(
                    str(wav_path),
                    language="es",
                    vad_filter=True,
                    beam_size=5,
                )
                segmentos = []
                for seg in segments_gen:
                    segmentos.append(seg)
                    progress.progress(
                        min(_segment_val(seg, "end") / dur, 1.0),
                        text=f" Transcribiendo… {min(_segment_val(seg,'end')/dur,1.0):.0%}",
                    )
            except RuntimeError as e:
                if "device-side assert triggered" in str(e):
                    st.warning(" Falla GPU; reintentando en CPU…")
                    cpu_model = WhisperModel("small", device="cpu", compute_type="int8")
                    segments_gen, _ = cpu_model.transcribe(
                        str(wav_path),
                        language="es",
                        vad_filter=True,
                        beam_size=5,
                    )
                    segmentos = list(segments_gen)

                else:
                    raise
            progress.empty()

            if not segmentos:
                st.warning(" No se detectó habla clara en el audio.")
                continue

            raw_text   = " ".join(_segment_text(s) for s in segmentos)
            texto_full = _dedupe(raw_text)
            st.success(" Transcripción completada")
            st.text_area(
                "Texto generado",
                texto_full,
                height=200,
                key=f"texto_{idx}",
            )

            with st.expander("Ver segmentos"):
                detalle = "\n".join(
                    f"[{_segment_val(s,'start'):.2f}s – {_segment_val(s,'end'):.2f}s] {_segment_text(s)}"
                    for s in segmentos
                )
                st.text_area(
                    "Segmentos",
                    detalle,
                    height=180,
                    key=f"segmentos_{idx}",
                )

            stem = Path(upl.name).stem
            txt_bytes = _export_txt(upl.name, fecha_hoy, texto_full)
            docx_bytes = _export_docx(upl.name, fecha_hoy, texto_full)

            st.download_button(
                "Descargar TXT",
                txt_bytes,
                file_name=f"{stem}.txt",
                mime="text/plain",
                key=f"txt_{idx}",
            )
            st.download_button(
                "Descargar DOCX",
                docx_bytes,
                file_name=f"{stem}.docx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                key=f"docx_{idx}",
            )

            zip_outputs.append({"name": f"{stem}.txt", "data": txt_bytes})
            zip_outputs.append({"name": f"{stem}.docx", "data": docx_bytes})

            reg_path = Path(UPLOAD_DIR) / "procesados.json"
            registro = []
            if reg_path.exists():
                try:
                    registro = json.loads(reg_path.read_text())
                except (ValueError, json.JSONDecodeError):
                    registro = []

            registro.append(
                {
                    "filename": upl.name,
                    "converted": str(wav_path),
                    "fecha": datetime.now().isoformat(),
                    "preview": texto_full[:100] + ("…" if len(texto_full) > 100 else ""),
                }
            )
            reg_path.write_text(json.dumps(registro, ensure_ascii=False, indent=2))

        if len(zip_outputs) > 2: 
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for item in zip_outputs:
                    zf.writestr(item["name"], item["data"])
            st.download_button(
                "Descargar todo en ZIP",
                zip_buf.getvalue(),
                file_name="transcripciones.zip",
                mime="application/zip",
            )

        removed = 0
        for f in Path(UPLOAD_DIR).iterdir():
            if f.suffix.lower() in {".mp3", ".wav", ".m4a"}:
                try:
                    f.unlink()
                    removed += 1
                except Exception as exc:
                    logging.warning("No se pudo eliminar %s: %s", f, exc)
        if removed:
            st.info(f"Se eliminaron {removed} archivos de audio temporales.")

    except Exception as exc:
        st.error(f"❌ Error inesperado: {exc}")
        logging.exception("Error crítico")
