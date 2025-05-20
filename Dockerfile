# AudioMate – Docker image con soporte GPU (CUDA 12 + PyTorch)
ARG PYTORCH_IMAGE_TAG=2.4.1-cuda12.1-cudnn9-runtime
FROM pytorch/pytorch:${PYTORCH_IMAGE_TAG}

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg libsndfile1 \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

RUN python3 - <<EOF
import whisper
whisper.load_model("base", device="cpu")
EOF

WORKDIR /app
COPY . /app

EXPOSE 8501
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
