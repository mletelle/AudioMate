import os
import json
import subprocess

def verificar_audio(path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-show_streams", "-print_format", "json", path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def test_verificar_audio_sample():
    path = "app/uploads/converted_test.wav"
    assert os.path.exists(path), f"No existe el archivo {path}"

    info = verificar_audio(path)
    assert float(info["format"]["duration"]) > 0
    assert int(info["streams"][0]["channels"]) in [1, 2]
    assert int(info["streams"][0]["sample_rate"]) in [16000, 44100]
