from dataclasses import dataclass
from typing import Callable

RISKS = ("safe", "confirm", "blocked")


@dataclass(frozen=True)
class CommandSpec:
    template: str                    # e.g. "list {ext} files"
    risk: str
    status: str
    build: Callable[..., list[str]]  # function that makes the argv list


_REGISTRY: dict[str, CommandSpec] = {}


def command(template: str, risk: str = "safe", status: str = ""):
    """Register a function as a voice command."""
    if risk not in RISKS:
        raise ValueError(f"risk must be one of {RISKS}, got {risk!r}")

    def decorator(func):
        _REGISTRY[template] = CommandSpec(template, risk, status or template, func)
        return func

    return decorator


def get_spec(template: str) -> CommandSpec | None:
    return _REGISTRY.get(template)


def all_specs() -> list[CommandSpec]:
    return list(_REGISTRY.values())


def clear() -> None:
    """Empty the registry (used by tests)."""
    _REGISTRY.clear()