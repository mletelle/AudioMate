# Usamos python:3.11-slim como base
FROM python:3.11-slim

# Instalación de FFmpeg y dependencias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# Instalamos dependencias de Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiamos el resto de la aplicación
COPY . /app

# Directorio de trabajo
WORKDIR /app

# Comando por defecto
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
