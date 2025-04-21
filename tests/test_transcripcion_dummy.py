import whisper

def test_transcribe_mock(monkeypatch):
    def fake_transcribe(path):
        return {"text": "Este es un texto de prueba", "segments": [{"start": 0, "end": 1, "text": "Prueba"}], "language": "es"}

    model = whisper.load_model("tiny")
    monkeypatch.setattr(model, "transcribe", fake_transcribe)

    result = model.transcribe("dummy_path.wav")
    assert "text" in result
    assert result["text"] == "Este es un texto de prueba"
