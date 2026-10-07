from dataclasses import dataclass

from .models import Command

# characters that let one command sneak in another (or expand variables)
FORBIDDEN_CHARS = set(';&|<>^%`$"\n\r\x00')


@dataclass(frozen=True)
class Decision:
    action: str  # "run", "confirm", or "blocked"
    reason: str  # shown in the overlay and written to the audit log


def check(command: Command) -> Decision:
    """Decide what to do with a Command. Fails closed."""
    if not command.argv:
        return Decision("blocked", "Empty command")

    for part in command.argv:
        bad = FORBIDDEN_CHARS.intersection(part)
        if bad:
            return Decision("blocked", f"Forbidden characters: {sorted(bad)}")

    if command.risk == "safe":
        return Decision("run", "Safe command")
    if command.risk == "confirm":
        return Decision("confirm", "Needs confirmation")
    if command.risk == "blocked":
        return Decision("blocked", "Command is blocked")

    return Decision("blocked", f"Unknown risk level: {command.risk!r}")