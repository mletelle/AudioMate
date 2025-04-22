# AudioMate

[![CI](https://img.shields.io/github/actions/workflow/status/mletelle/audiomate/ci.yml?branch=main)]() 
[![Codecov](https://img.shields.io/codecov/c/github/mletelle/AudioMate/main.svg)](https://codecov.io/gh/mletelle/AudioMate)
[![Docker Pulls](https://img.shields.io/docker/pulls/mletelle/audiomate?cacheSeconds=300)](https://hub.docker.com/r/mletelle/audiomate)
[![License](https://img.shields.io/github/license/mletelle/audiomate)]()

**AudioMate** es una aplicación web local que te permite transcribir archivos de audio (MP3, WAV, M4A) a texto usando **OpenAI Whisper** y **Streamlit**.  
Ideal para estudiantes, profesionales e investigadores que necesitan generar transcripciones offline en TXT y DOCX.

---

## Tabla de contenidos

1. [Características](#-características)   
2. [Requisitos](#-requisitos)  
3. [Instalación](#-instalación)  
   - [Con Docker + GPU (recomendado)](#con-docker--gpu-recomendado)  
   - [Con Docker (solo CPU)](#con-docker-solo-cpu)  
4. [Uso](#-uso)  
5. [Configuración](#-configuración)  
6. [Estructura del proyecto](#-estructura-del-proyecto)  
7. [Pruebas](#-pruebas)  
8. [Troubleshooting](#-troubleshooting)  
9. [Contribuir](#-contribuir)  
10. [Licencia](#-licencia)

---

##  Características

- **100% Offline**: no dependés de servicios externos.  
- **Soporta MP3, WAV y M4A** → convierte internamente a WAV mono 16 kHz.  
- Interfaz web sencilla con **Streamlit**.  
- Exportación a **.txt** y **.docx**.  
- **GPU-ready**: acelera Whisper usando tu tarjeta NVIDIA.  
- Listo para **Docker**: clonar y levantar con un solo comando.  
- **Modular** y **escalable**: pensado para producción y CI/CD.

---

##  Requisitos

- **Hardware**: CPU mínimo i5 o R7, GPU NVIDIA (opcional pero recomendado).  
- **Software**:  
  - Docker **>= 20.10**  
  - Docker Compose **v2** (plugin `docker compose`)  
  - (solo GPU) NVIDIA Driver **>= 535**, `nvidia-container-toolkit`  

---

##  Instalación

### 1. Con Docker + GPU (recomendado)

```bash
# 1. Clonar repo
git clone https://github.com/mletelle/audiomate.git
cd audiomate

# 2. Instalar nvidia-container-toolkit (una sola vez)
#    ver sección "Configuración" más abajo

# 3. Build & up
docker compose up -d --build
````
Luego abrí en tu navegador: http://localhost:8501

### 2. Con Docker (solo CPU)
Si no tenés GPU o no querés configurar CUDA:
```bash
# 1. Clonar repo
git clone https://github.com/mletelle/audiomate.git
cd audiomate

# 2. Build & up
docker compose -f docker-compose.cpu.yml up -d --build
```
>NOTA: previamente deberás cambiar la imagen base en Dockerfile a python:3.11-slim y forzar --device=cpu en Whisper

---
## Uso
1. Subí tu archivo de audio (MP3, WAV o M4A).
2. Esperá mientras:
    - FFmpeg convierte a WAV mono 16 kHz.
    - Whisper transcribe (GPU o CPU).
3. Descargá tu transcripción en TXT o DOCX.
4. Opcional: revisá el historial en uploads/procesados.json.

---
## Configuración
Variables de entorno (opcional)
Variable | Descripción | Valor por defecto
|--|--|--|
MAX_FILE_SIZE | Tamaño máximo de subida (bytes) | 200*1024*1024 (200 MB)
WHISPER_MODEL | Modelo Whisper a cargar (tiny, base, etc.) | base
PYTHONUNBUFFERED | Unbuffered I/O | 1

---
## Instalación nvidia‑container‑toolkit
````bash
# Asumiendo Ubuntu 22.04 / 20.04
sudo apt-get update && sudo apt-get install -y curl gnupg lsb-release
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
  | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit.gpg
dist=$(. /etc/os-release; echo $ID$VERSION_ID)
curl -sL https://nvidia.github.io/libnvidia-container/$dist/libnvidia-container.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit.gpg] https://#' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
# test
docker run --rm --gpus all nvidia/cuda:12.3.1-base nvidia-smi
````

---
## Troubleshooting
Síntoma | Solución rápida
|--|--|
CUDA not available | Verificá docker compose run --rm audiomate python -c "import torch; print(torch.cuda.is_available())"
ffmpeg: command not found | Asegurate de rebuildear la imagen (docker compose up --build).
App no carga en 8501 | Verificá firewall / puerto ocupado y revisá logs: docker compose logs -f audiomate.
JSON corrupto en procesados.json | Se auto-repara al arrancar; si persiste, borrá ese archivo manualmente.
