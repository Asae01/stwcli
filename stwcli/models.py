from dataclasses import dataclass


@dataclass
class Command:
    heard: str        # what the user said
    argv: list[str]   # the real command, as a list (never one long string)
    risk: str         # "safe", "confirm", or "blocked"
    status: str       # text for the overlay, e.g. "Finding notes.txt"