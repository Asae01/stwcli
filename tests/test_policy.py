import pytest

from stwcli.models import Command
from stwcli.policy import check


def make(argv, risk="safe"):
    return Command(heard="test", argv=argv, risk=risk, status="test")


def test_safe_runs():
    assert check(make(["cmd", "/c", "dir"])).action == "run"


def test_confirm_asks():
    decision = check(make(["cmd", "/c", "del", "a.txt"], risk="confirm"))
    assert decision.action == "confirm"


def test_blocked_is_refused():
    assert check(make(["cmd", "/c", "dir"], risk="blocked")).action == "blocked"


def test_unknown_risk_fails_closed():
    assert check(make(["cmd", "/c", "dir"], risk="yolo")).action == "blocked"


def test_empty_argv_is_blocked():
    assert check(make([])).action == "blocked"


@pytest.mark.parametrize(
    "bad", ["a;b", "a&b", "a|b", "a>b", "a<b", "a^b", "%PATH%", "a`b", "$x", 'a"b', "a\nb"]
)
def test_forbidden_chars_are_blocked(bad):
    assert check(make(["cmd", "/c", "dir", bad])).action == "blocked"


def test_forbidden_chars_block_even_confirm_tier():
    decision = check(make(["cmd", "/c", "del", "a&calc"], risk="confirm"))
    assert decision.action == "blocked"