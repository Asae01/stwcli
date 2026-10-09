# stwcli
Lightweight voice-controlled terminal helper

stwcli is a lightweight, offline voice-controlled terminal helper. You speak a
command, it shows what it understood, checks it against a safety policy, and
only then runs it.

## Setup: speech model

stwcli uses [Vosk](https://alphacephei.com/vosk/) for offline speech recognition.
The model is not included in the repo (it is about 40 MB).

1. Download `vosk-model-small-en-us-0.15` from https://alphacephei.com/vosk/models
2. Extract it so this folder exists: `models/vosk-model-small-en-us-0.15/`

The `models/` folder is ignored by git.