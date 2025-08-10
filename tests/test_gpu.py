# tests/test_gpu.py
import torch
from faster_whisper import WhisperModel
import os

def test_gpu_model_loading():
    """
    Verifica la disponibilidad de CUDA y carga un modelo de faster-whisper
    en el dispositivo correspondiente (GPU o CPU).
    """
    print("--- Verificación de Dispositivo y Modelo ---")

    cuda_available = torch.cuda.is_available()
    print(f" CUDA disponible: {cuda_available}")

    if cuda_available:
        print(f" Dispositivo GPU: {torch.cuda.get_device_name(0)}")
        device = "cuda"
        compute_type = "float16"
    else:
        print(" Usando CPU.")
        device = "cpu"
        compute_type = "int8"

    print(" Cargando modelo faster-whisper (tiny)...")
    cache_dir = os.getenv("WHISPER_CACHE", "/root/.cache/whisper")
    
    model = None
    try:
        model = WhisperModel(
            "tiny",
            device=device,
            compute_type=compute_type,
            download_root=cache_dir
        )
    except Exception as e:
        assert False, f"La carga del modelo falló con la excepción: {e}"

    assert model is not None, "El objeto del modelo no debería ser None después de la carga."
    print(f" Modelo cargado exitosamente.")