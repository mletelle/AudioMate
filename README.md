# AudioMate – Conversor de Audio a Texto con Whisper y Streamlit 

---
AudioMate es una aplicación web gratuita, liviana y completamente local que permite a estudiantes, profesionales e investigadores convertir fácilmente grabaciones de audio (MP3, WAV, M4A) en texto. 
Desarrollada con Python, Streamlit y Whisper (OpenAI), permite una transcripción sin conexión a internet, con posibilidad de descargar el resultado en formatos .txt o .docx.
- 100% offline: Usa Whisper localmente sin depender de APIs externas.
- Soporta múltiples formatos: MP3, WAV, M4A → WAV mono 16 kHz.
- Interfaz simple y clara: Desarrollada con Streamlit.
- Descargas disponibles: Exporta transcripciones en .txt y .docx.
- Organización modular y escalable: Proyecto estructurado y dockerizado.
- Docker listo: Levantá todo tu entorno con un solo comando.
---
## Instalación rápida
- Prerequisitos: Docker Desktop y Git
````bash
# 1. Clona el repositorio
git clone https://github.com/<tu_usuario>/AudioMate.git
cd AudioMate
# 2. Levantá el entorno con Docker Compose
docker-compose up --build
````
> ⚠️ **Importante:** la primera vez que ejecutes `docker-compose up --build`, la construcción de la imagen puede tardar **20-40 minutos**, dependiendo de tu conexión a Internet y la potencia de tu equipo.  
> Esto se debe a que se descargan librerías pesadas como `torch`, `nvidia-cusparse`, `ffmpeg` y otras dependencias de audio y GPU.
> Una vez construido, los siguientes levantamientos serán mucho más rápidos gracias al cache de Docker 🐳.

- Listo! Abrí tu navegador en: http://localhost:8501 

---
## Uso paso a paso
1. Subí tu archivo de audio
    - Formatos soportados: MP3, WAV, M4A
    - Tamaño máximo: 200 MB
2. Transcribí automáticamente 
    - AudioMate convierte tu audio automáticamente a WAV mono (16 kHz)
    - Whisper genera la transcripción localmente.
3. Descargá tu texto 
    - Disponibles formatos:
      - .txt (texto simple)
      - .docx (Word)

---
## Querés contribuir?
  - Hacé fork del repositorio. Crea tu rama. Commitea, pusheá y abri pull request

---
## Documentación y soporte
Si tenés dudas o sugerencias:
  - Abrí un issue en este repo.
  - Consultá la documentación oficial de Streamlit
  - Revisá la documentación oficial de Whisper
