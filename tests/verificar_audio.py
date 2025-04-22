import wave

@pytest.fixture(scope="session", autouse=True)
def create_dummy_wav(tmp_path_factory):
    dest = tmp_path_factory.mktemp("uploads") / "converted_test.wav"
    # Generamos 1s de silencio a 16 kHz mono
    with wave.open(str(dest), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(b"\x00\x00" * 16000)
    # copiamos al UPLOAD_DIR de la app
    shutil.copy(str(dest), os.path.join(UPLOAD_DIR, "converted_test.wav"))
    yield
    dest.unlink()
