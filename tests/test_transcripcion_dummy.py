# tests/test_transcripcion_dummy.py
from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment

def test_transcribe_mock(monkeypatch):
    """
    Prueba la transcripción simulando la salida de faster_whisper.
    """
    def fake_transcribe(path, **kwargs):
        # La salida de faster_whisper es un generador de objetos Segment
        def segment_generator():
            yield Segment(start=0.0, end=1.0, text="Prueba")
        
        # El segundo valor de retorno es un objeto Info con el idioma
        class MockInfo:
            language = "es"
            language_probability = 0.99
        
        return segment_generator(), MockInfo()

    # Se necesita un modelo real para aplicar el monkeypatch
    model = WhisperModel("tiny", device="cpu")
    monkeypatch.setattr(model, "transcribe", fake_transcribe)

    segments, info = model.transcribe("dummy_path.wav")
    
    # El resultado es un generador, lo convertimos a lista para verificarlo
    result_list = list(segments)
    full_text = " ".join([seg.text for seg in result_list])

    assert info.language == "es"
    assert "Prueba" in full_text