from rapidfuzz import fuzz

from .models import Command
from .registry import CommandSpec, all_specs

THRESHOLD = 80  # how close a fixed word must be (0-100)

# spoken word -> value the command needs
ALIASES = {"python": "py", "text": "txt"}


def _is_slot(token: str) -> bool:
    return token.startswith("{") and token.endswith("}")


def _match(spec: CommandSpec, words: list[str]):
    """Return (score, slots) if the words fit this phrase, else None."""
    tokens = spec.template.split()

    if _is_slot(tokens[-1]):
        # a final slot can swallow the rest of the sentence ("my notes.txt")
        if len(words) < len(tokens):
            return None
        words = words[: len(tokens) - 1] + [" ".join(words[len(tokens) - 1 :])]
    elif len(words) != len(tokens):
        return None

    slots: dict[str, str] = {}
    scores: list[float] = []
    for token, word in zip(tokens, words):
        if _is_slot(token):
            slots[token[1:-1]] = ALIASES.get(word, word)  # copied, not fuzzed
        else:
            score = fuzz.ratio(token, word)
            if score < THRESHOLD:
                return None
            scores.append(score)

    average = sum(scores) / len(scores) if scores else 100.0
    return average, slots


def parse(text: str) -> Command | None:
    """Turn a sentence into a Command, or None if not understood."""
    words = text.lower().strip().strip(".,!?").split()
    if not words:
        return None

    best = None
    for spec in all_specs():
        result = _match(spec, words)
        if result and (best is None or result[0] > best[0]):
            best = (result[0], spec, result[1])

    if best is None:
        return None

    _, spec, slots = best
    return Command(
        heard=text,
        argv=spec.build(**slots),
        risk=spec.risk,
        status=spec.status.format(**slots),
    )