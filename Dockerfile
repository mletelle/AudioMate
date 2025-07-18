#  AudioMate GPU 
ARG PYTORCH_TAG=2.4.0-cuda12.4-cudnn9-runtime
FROM pytorch/pytorch:${PYTORCH_TAG}

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    # rutas de caché locales
    TORCH_HOME=/root/.cache/torch \
    WHISPER_CACHE=/root/.cache/whisper

# ffmpeg , libsndfile)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

# dependencias 
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# precarga 
RUN CUDA_VISIBLE_DEVICES="" python - <<'PY'
import faster_whisper, os
_ = faster_whisper.WhisperModel(
    "large-v2",
    device="cpu",
    compute_type="int8",
    download_root=os.environ["WHISPER_CACHE"]
)
PY

WORKDIR /app
COPY . /app

EXPOSE 8501
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
