import json
from datetime import datetime
from pathlib import Path

DEFAULT_PATH = Path.home() / ".stwcli" / "audit.log"

EVENTS = ("heard", "not_understood", "blocked", "cancelled", "executed")


def log(event, *, heard="", argv=None, detail="", path=None):
    """Append one JSON line to the audit log."""
    if event not in EVENTS:
        raise ValueError(f"event must be one of {EVENTS}, got {event!r}")

    path = Path(path) if path else DEFAULT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "time": datetime.now().astimezone().isoformat(timespec="seconds"),
        "event": event,
        "heard": heard,
        "argv": argv or [],
        "detail": detail,
    }
    with open(path, "a", encoding="utf-8") as file:
        file.write(json.dumps(entry, ensure_ascii=False) + "\n")