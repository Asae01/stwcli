import json
from pathlib import Path

from vosk import KaldiRecognizer, Model, SetLogLevel

from .audio import SAMPLE_RATE

DEFAULT_MODEL = (
    Path(__file__).resolve().parent.parent / "models" / "vosk-model-small-en-us-0.15"
)

SetLogLevel(-1)  # silence Vosk's chatty logging


class SttError(Exception):
    """Raised when speech recognition can't be set up."""


class Transcriber:
    def __init__(self, model_path=None):
        path = Path(model_path) if model_path else DEFAULT_MODEL
        if not path.is_dir():
            raise SttError(
                f"Vosk model not found at {path}. See the README for download steps."
            )
        self._model = Model(str(path))  # loaded once, reused for every command

    def transcribe(self, audio: bytes) -> str:
        """Turn raw 16 kHz mono 16-bit audio into text."""
        recognizer = KaldiRecognizer(self._model, SAMPLE_RATE)
        recognizer.AcceptWaveform(audio)
        result = json.loads(recognizer.FinalResult())
        return result.get("text", "").strip()