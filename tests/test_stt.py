import json

import pytest

from stwcli import stt


class FakeModel:
    count = 0

    def __init__(self, path):
        FakeModel.count += 1


class FakeRecognizer:
    last = None
    text = "  list python files "

    def __init__(self, model, rate):
        self.rate = rate
        self.fed = b""
        FakeRecognizer.last = self

    def AcceptWaveform(self, data):
        self.fed += data
        return True

    def FinalResult(self):
        return json.dumps({"text": FakeRecognizer.text})


@pytest.fixture(autouse=True)
def fake_vosk(monkeypatch):
    FakeModel.count = 0
    FakeRecognizer.text = "  list python files "
    monkeypatch.setattr(stt, "Model", FakeModel)
    monkeypatch.setattr(stt, "KaldiRecognizer", FakeRecognizer)


def test_missing_model_gives_clear_error(tmp_path):
    with pytest.raises(stt.SttError) as info:
        stt.Transcriber(model_path=tmp_path / "nope")
    assert "model" in str(info.value).lower()


def test_transcribe_returns_clean_text(tmp_path):
    transcriber = stt.Transcriber(model_path=tmp_path)
    assert transcriber.transcribe(b"\x00\x00") == "list python files"


def test_model_is_loaded_only_once(tmp_path):
    transcriber = stt.Transcriber(model_path=tmp_path)
    transcriber.transcribe(b"\x00\x00")
    transcriber.transcribe(b"\x00\x00")
    assert FakeModel.count == 1


def test_empty_result_gives_empty_string(tmp_path):
    FakeRecognizer.text = ""
    transcriber = stt.Transcriber(model_path=tmp_path)
    assert transcriber.transcribe(b"") == ""


def test_audio_is_fed_at_16khz(tmp_path):
    transcriber = stt.Transcriber(model_path=tmp_path)
    transcriber.transcribe(b"\x01\x02")
    assert FakeRecognizer.last.rate == 16000
    assert FakeRecognizer.last.fed == b"\x01\x02"