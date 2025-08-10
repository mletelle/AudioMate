# tests/test_transcripcion_dummy.py
from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment

def test_transcribe_mock(monkeypatch):
    """
    Prueba la transcripción simulando (mocking) la salida de faster_whisper.
    """
    def fake_transcribe(path, **kwargs):
        def segment_generator():
            yield Segment(start=0.0, end=1.0, text="Texto de prueba")
        
        class MockInfo:
            language = "es"
            language_probability = 0.99
        
        return segment_generator(), MockInfo()

    model = WhisperModel("tiny", device="cpu")
    monkeypatch.setattr(model, "transcribe", fake_transcribe)

    segments, info = model.transcribe("dummy_path.wav")
    
    result_list = list(segments)
    full_text = " ".join([seg.text for seg in result_list])

    assert info.language == "es"
    assert "Texto de prueba" in full_text