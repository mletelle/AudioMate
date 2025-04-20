# STT
---
## Descripción General: 
Crear una aplicación web gratuita que permita a estudiantes o profesionales subir grabaciones de audio (MP3, WAV, etc.) y obtener a cambio una transcripción textual descargable en formatos como .txt o .docx.

---
## Objetivos
- Principal: Automatizar la conversión de audio a texto usando herramientas open‑source.
- Secundarios:
  - Ofrecer descarga de la transcripción en varios formatos.
  - En futuras versiones, enriquecer el texto (resúmenes, resaltados, exportación a Google Docs).

---
## Público Objetivo
- Estudiantes que graban clases o conferencias.
- Profesionales que registran reuniones largas.
- Periodistas o investigadores que necesitan un guión textual de entrevistas.
- Personas con TDAH o dislexia que prefieren leer la información.

---
## Problemática
- Volver a escuchar horas de audio es lento y poco práctico.
- Tomar notas manualmente interfiere con la atención durante la grabación.
- Falta de soluciones gratuitas y auto‑alojadas para transcribir localmente.

---
## Solución Propuesta
Una app web local (o desplegable en VPS) basada en Django que:
1. Recibe un archivo de audio (MP3, M4A, WAV…).
2. Convierte, si hace falta, a formato compatible (WAV) con ffmpeg.
3. Llama a Whisper (modelo “base” o “small”) para generar la transcripción.
4. Muestra el texto en pantalla y permite descargarlo en .txt o .docx.

---
## Tech Stack & Herramientas
- Backend:	Python + Django
- Frontend:	HTML5, CSS3, JavaScript
- Transcripción de voz:	Whisper open‑source (pip install openai‑whisper)
- Procesamiento de audio:	ffmpeg + pydub
- Exportar a .docx:	python-docx
- Almacenamiento temporal:	Sistema de archivos local + SQLite
- Contenerización:	Docker & Docker Compose
- Servidor web:	NGINX (as reverse proxy)
- (Futuro) Mejora de texto:	OpenAI GPT/ChatGPT API (resúmenes, correcciones)

---
## Principales Funcionalidades
- Subida de audio: 
Formulario web con validación de tipo y tamaño.
- Conversión de formato: 
ffmpeg en background para asegurar compatibilidad con Whisper.
- Transcripción: 
Ejecución de Whisper en Python (sin llamadas a Internet).
- Visualización & Descarga: 
Área de texto resultante + botones para descargar .txt y .docx.

---
## Ideas de Funcionalidades Extra
- Detección automática de idioma para elegir el modelo adecuado.
- Resumen por bloques usando GPT (v.2).
- Etiquetas/keywords (e.g. “importante”, “examen”).
- Organizador: agrupar transcripciones por fecha o materia.
- Exportación a Google Docs (integración OAuth).

---
## Casos de Uso Reales
- Revisión rápida de apuntes antes de un examen.
- Documentación de actas de reuniones para RRHH o gerencia.
- Transformar entrevistas en texto para investigación cualitativa.

---
## Arquitectura de Alto Nivel
````mermaid
flowchart LR
  A[Usuario] --> B(Django: Formulario)
  B --> C{Archivo subido}
  C -->|Convierte MP3→WAV| D[ffmpeg/pydub container]
  D -->|Invoca| E[Whisper container]
  E --> F[Texto transcripción]
  F --> G[Django: Guardar y mostrar]
  G --> H[Descarga TXT]
````
- Contenedor app: Django + Gunicorn, gestiona vistas, subida y descargas.
- Contenedor ffmpeg: imagen ligera con ffmpeg y pydub.
- Contenedor whisper: Python, whisper, torch y dependencias GPU si disponible.
- Contenedor nginx: pone frente al app para servir estáticos y proxy.

---
## Roadmap de Implementación de primera fase
- Docker Compose inicial: definir servicios app, ffmpeg, whisper y nginx.
- Skeleton Django: crear proyecto y app, media/ para subidas.
- Formulario de upload: vista + template + manejo de archivos.
- Conversión de audio: test local con pydub + ffmpeg.
- Integración Whisper: crear función Python que reciba ruta de WAV y devuelva string.
- Mostrar y descargar: vista que renderiza texto y enlace a .txt.
- Despliegue local

---
## Fases 
- V1 (MVP (versión 1.0)):
  - Subida de archivo MP3/MP4 vía formulario web.
  - Conversión automática a WAV (ffmpeg).
  - Transcripción local con Whisper (modelo base).
  - Visualización del texto en pantalla.
  - Descarga de la transcripción en .txt.
- V2:
  - Añadir descarga en .docx
  - División por bloques de tiempo.
  - Detección automática de idioma (Whisper lo soporta por defecto).
- V3:
  - Integración GPT para resumen y mejora, detección de idioma.
  - Autenticación de usuarios y almacenamiento de histórico.
  - Etiquetado de palabras clave y marcado de “puntos importantes”.
  - Integración con Google Calendar o exportación a Google Docs.

