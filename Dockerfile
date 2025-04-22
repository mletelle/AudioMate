# ────────────────────────────────────────────────────────────────────
#  AudioMate – Docker image con soporte GPU (CUDA 12 + PyTorch)
#  Basado en la imagen oficial «pytorch/pytorch» para evitar reinstalar
#  torch/cuDNN en cada build y así acelerar el tiempo de construcción.
# ────────────────────────────────────────────────────────────────────
ARG PYTORCH_IMAGE_TAG=2.4.1-cuda12.1-cudnn9-runtime           # ver: :contentReference[oaicite:0]{index=0}
FROM pytorch/pytorch:${PYTORCH_IMAGE_TAG}

# ——— variables gDlobales ————————————————————————————————
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# ——— dependencias del sistema (ffmpeg + libsndfile) ——————————
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg libsndfile1 \
 && rm -rf /var/lib/apt/lists/*

# ——— instalación de librerías Python ————————————————
# 1) copiamos solo requirements para aprovechar la cache
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
 && rm -f /tmp/requirements.txt

# ——— copiado de la app (último paso ⇒ invalidación mínima) ————
WORKDIR /app
COPY . /app

EXPOSE 8501
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
