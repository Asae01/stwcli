import pytest

from stwcli import registry
from stwcli.parser import parse
from stwcli.registry import command


@pytest.fixture(autouse=True)
def commands():
    registry.clear()

    @command("list {ext} files", risk="safe", status="Listing {ext} files")
    def list_files(ext):
        return ["cmd", "/c", "dir", f"*.{ext}"]

    @command("find {name}", risk="safe", status="Finding {name}")
    def find_file(name):
        return ["cmd", "/c", "dir", "/s", "/b", name]

    yield
    registry.clear()


def test_exact_phrase_fills_slot():
    cmd = parse("list python files")
    assert cmd is not None
    assert cmd.argv == ["cmd", "/c", "dir", "*.py"]
    assert cmd.status == "Listing py files"
    assert cmd.heard == "list python files"


def test_typo_still_matches():
    cmd = parse("lst python fils")
    assert cmd is not None
    assert cmd.argv[-1] == "*.py"


def test_unknown_phrase_returns_none():
    assert parse("make me a sandwich") is None
    assert parse("dance wildly now") is None


def test_empty_input_returns_none():
    assert parse("") is None
    assert parse("   ") is None


def test_slot_values_are_not_fuzzy_corrected():
    cmd = parse("find lists.txt")
    assert cmd is not None
    assert cmd.argv[-1] == "lists.txt"