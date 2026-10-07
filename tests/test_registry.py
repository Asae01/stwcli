import pytest

from stwcli import registry
from stwcli.registry import command


@pytest.fixture(autouse=True)
def clean_registry():
    registry.clear()
    yield
    registry.clear()


def test_command_is_registered():
    @command("list {ext} files", risk="safe", status="Listing {ext} files")
    def list_files(ext):
        return ["cmd", "/c", "dir", f"*.{ext}"]

    spec = registry.get_spec("list {ext} files")
    assert spec is not None
    assert spec.risk == "safe"
    assert spec.build("py") == ["cmd", "/c", "dir", "*.py"]


def test_invalid_risk_is_rejected():
    with pytest.raises(ValueError):
        @command("do thing", risk="yolo")
        def do_thing():
            return []


def test_status_defaults_to_template():
    @command("show files")
    def show_files():
        return ["cmd", "/c", "dir"]

    assert registry.get_spec("show files").status == "show files"