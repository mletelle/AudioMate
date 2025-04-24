import os
import wave
import subprocess
import json

def verificar_audio(path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_format",
        "-show_streams",
        "-print_format", "json",
        path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)

def test_verificar_audio_ci(tmp_path):
    # 1. Genero un WAV mono de 1 segundo a 16 kHz
    wav_file = tmp_path / "ci_test.wav"
    with wave.open(str(wav_file), 'w') as wf:
        wf.setnchannels(1)         # mono
        wf.setsampwidth(2)         # 16 bits = 2 bytes
        wf.setframerate(16000)     # 16 kHz
        wf.writeframes(b'\x00\x00' * 16000)  # 1 segundo de silencio

    # 2. Aseguro que existe
    assert os.path.exists(wav_file), f"No existe el archivo {wav_file}"

    # 3. Verifico con ffprobe
    info = verificar_audio(str(wav_file))
    # compruebo duración, canales y sample rate
    assert float(info["format"]["duration"]) > 0
    assert int(info["streams"][0]["channels"]) == 1
    assert int(info["streams"][0]["sample_rate"]) == 16000
