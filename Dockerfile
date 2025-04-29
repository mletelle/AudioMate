# ────────────────────────────────────────────────────────────────────
# AudioMate – Docker image con soporte GPU (CUDA 12 + PyTorch)
# ────────────────────────────────────────────────────────────────────
ARG PYTORCH_IMAGE_TAG=2.4.1-cuda12.1-cudnn9-runtime
FROM pytorch/pytorch:${PYTORCH_IMAGE_TAG}

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Instalación de ffmpeg y libsndfile
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg libsndfile1 \
 && rm -rf /var/lib/apt/lists/*

# Copio y monto requirements para cachear pip
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

# ── Aquí pre-descargamos Whisper para que en runtime no haga pull ──
RUN python3 - <<EOF
import whisper
# Carga el modelo base en CPU y lo guarda en ~/.cache/whisper
whisper.load_model("base", device="cpu")
EOF

# Copio el resto de la app
WORKDIR /app
COPY . /app

EXPOSE 8501
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
