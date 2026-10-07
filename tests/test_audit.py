import json

import pytest

from stwcli.audit import log


def read(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_log_writes_one_json_line(tmp_path):
    path = tmp_path / "audit.log"
    log("executed", heard="list python files", argv=["cmd", "/c", "dir", "*.py"], path=path)
    entries = read(path)
    assert len(entries) == 1
    assert entries[0]["event"] == "executed"
    assert entries[0]["heard"] == "list python files"
    assert entries[0]["argv"] == ["cmd", "/c", "dir", "*.py"]
    assert "time" in entries[0]


def test_log_appends_and_never_overwrites(tmp_path):
    path = tmp_path / "audit.log"
    log("heard", heard="one", path=path)
    log("blocked", heard="two", detail="Forbidden characters", path=path)
    assert [e["event"] for e in read(path)] == ["heard", "blocked"]


def test_blocked_and_cancelled_are_logged(tmp_path):
    path = tmp_path / "audit.log"
    log("blocked", heard="bad", detail="Refused by policy", path=path)
    log("cancelled", heard="delete notes", path=path)
    assert [e["event"] for e in read(path)] == ["blocked", "cancelled"]


def test_unknown_event_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        log("oops", path=tmp_path / "audit.log")


def test_missing_folder_is_created(tmp_path):
    path = tmp_path / "nested" / "audit.log"
    log("heard", heard="hi", path=path)
    assert path.exists()


def test_newlines_cannot_forge_entries(tmp_path):
    path = tmp_path / "audit.log"
    log("heard", heard='hi\n{"event": "executed"}', path=path)
    assert len(read(path)) == 1