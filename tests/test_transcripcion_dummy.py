# tests/test_transcripcion_dummy.py
from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment, Word

def test_transcribe_mock(monkeypatch):
    """
    Prueba la transcripción simulando (mocking) la salida de faster_whisper.
    """
    def fake_transcribe(path, **kwargs):
        def segment_generator():
            # Se instancian los 'Word' objects requeridos por el 'Segment'
            mock_words = [Word(start=0.0, end=0.5, word="Texto", probability=0.9),
                          Word(start=0.5, end=1.0, word="de", probability=0.9),
                          Word(start=1.0, end=1.5, word="prueba", probability=0.9)]

            yield Segment(
                start=0.0,
                end=1.5,
                text="Texto de prueba",
                # Se añaden los argumentos requeridos con valores simulados
                id=0,
                seek=0,
                tokens=[50257, 123, 456, 789, 50364],
                avg_logprob=-0.5,
                compression_ratio=1.5,
                no_speech_prob=0.1,
                words=mock_words,
                temperature=0.0
            )

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
    assert len(result_list) == 1, "El generador debería haber producido un solo segmento."
    segment = result_list[0]
    assert hasattr(segment, 'words') and len(segment.words) > 0, "El segmento debe contener una lista de palabras."