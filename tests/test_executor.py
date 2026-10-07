import subprocess
import sys

from stwcli.executor import run
from stwcli.models import Command


def make(argv, risk="safe"):
    return Command(heard="test", argv=argv, risk=risk, status="test")


def test_captures_stdout():
    result = run(make([sys.executable, "-c", "print('hello')"]))
    assert result.stdout.strip() == "hello"
    assert result.returncode == 0


def test_captures_stderr_and_exit_code():
    result = run(make([sys.executable, "-c", "raise SystemExit('oops')"]))
    assert "oops" in result.stderr
    assert result.returncode == 1


def test_timeout_is_enforced():
    result = run(make([sys.executable, "-c", "__import__('time').sleep(5)"]), timeout=0.5)
    assert result.returncode == -1
    assert "Timed out" in result.stderr


def test_missing_program_is_reported():
    result = run(make(["definitely-not-a-real-program"]))
    assert result.returncode == -1
    assert "not found" in result.stderr.lower()


def test_never_uses_shell(monkeypatch):
    seen = {}

    def fake_run(*args, **kwargs):
        seen.update(kwargs)
        return subprocess.CompletedProcess(args[0], 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    run(make(["echo", "hi"]))
    assert seen.get("shell") is False


def test_blocked_by_policy_never_runs():
    result = run(make(["cmd", "/c", "dir", "a&calc"]))
    assert result.returncode == -1
    assert "policy" in result.stderr.lower()