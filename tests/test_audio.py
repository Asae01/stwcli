import pytest

from stwcli import audio


class FakeStream:
    last = None

    def __init__(self, samplerate, channels, dtype, callback):
        self.settings = (samplerate, channels, dtype)
        self.callback = callback
        self.closed = False
        FakeStream.last = self

    def start(self):
        pass

    def stop(self):
        pass

    def close(self):
        self.closed = True


def test_recorder_returns_bytes_in_vosk_format(monkeypatch):
    monkeypatch.setattr(audio.sd, "RawInputStream", FakeStream)
    recorder = audio.Recorder()
    recorder.start()
    FakeStream.last.callback(b"\x01\x02", 1, None, None)
    FakeStream.last.callback(b"\x03\x04", 1, None, None)
    data = recorder.stop()
    assert data == b"\x01\x02\x03\x04"
    assert FakeStream.last.settings == (16000, 1, "int16")
    assert FakeStream.last.closed


def test_no_microphone_gives_clear_error(monkeypatch):
    def broken(*args, **kwargs):
        raise audio.sd.PortAudioError("no device")

    monkeypatch.setattr(audio.sd, "RawInputStream", broken)
    with pytest.raises(audio.MicError) as info:
        audio.Recorder().start()
    assert "microphone" in str(info.value).lower()


def test_stop_without_start_is_an_error():
    with pytest.raises(audio.MicError):
        audio.Recorder().stop()


def test_double_start_is_an_error(monkeypatch):
    monkeypatch.setattr(audio.sd, "RawInputStream", FakeStream)
    recorder = audio.Recorder()
    recorder.start()
    with pytest.raises(audio.MicError):
        recorder.start()


def test_record_runs_for_given_seconds(monkeypatch):
    monkeypatch.setattr(audio.sd, "RawInputStream", FakeStream)
    slept = []

    def fake_sleep(seconds):
        slept.append(seconds)
        FakeStream.last.callback(b"\x00\x00", 1, None, None)

    monkeypatch.setattr(audio.time, "sleep", fake_sleep)
    data = audio.record(2)
    assert slept == [2]
    assert data == b"\x00\x00"