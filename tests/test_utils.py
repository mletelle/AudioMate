import re

def is_audio_file(filename):
    return bool(re.match(r".*\.(mp3|wav)$", filename, re.IGNORECASE))

def test_is_audio_file():
    assert is_audio_file("prueba.mp3")
    assert is_audio_file("audio.WAV")
    assert not is_audio_file("imagen.png")
