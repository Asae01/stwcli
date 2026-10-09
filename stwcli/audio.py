import time

import sounddevice as sd

SAMPLE_RATE = 16000  # Vosk wants 16 kHz
CHANNELS = 1         # mono
DTYPE = "int16"      # 16-bit audio


class MicError(Exception):
    """Raised when the microphone can't be used."""


class Recorder:
    def __init__(self):
        self._chunks: list[bytes] = []
        self._stream = None

    def _callback(self, indata, frames, time_info, status):
        self._chunks.append(bytes(indata))  # copy this slice of audio

    def start(self):
        if self._stream is not None:
            raise MicError("Already recording")
        self._chunks = []
        try:
            self._stream = sd.RawInputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype=DTYPE,
                callback=self._callback,
            )
            self._stream.start()
        except (sd.PortAudioError, ValueError) as error:
            self._stream = None
            raise MicError(f"Could not open the microphone: {error}") from error

    def stop(self) -> bytes:
        if self._stream is None:
            raise MicError("Not recording")
        self._stream.stop()
        self._stream.close()
        self._stream = None
        return b"".join(self._chunks)


def record(seconds: float) -> bytes:
    """Record for a fixed number of seconds and return the raw audio."""
    recorder = Recorder()
    recorder.start()
    try:
        time.sleep(seconds)
    finally:
        audio = recorder.stop()  # always release the mic, even on Ctrl+C
    return audio