import torch
import whisper

print("🧠 CUDA disponible:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("🚀 Dispositivo:", torch.cuda.get_device_name(0))
    device = "cuda"
else:
    device = "cpu"

print("📦 Cargando modelo Whisper...")
model = whisper.load_model("base", device=device)
print("✅ Modelo cargado en:", next(model.parameters()).device)
