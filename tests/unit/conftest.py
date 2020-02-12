import pytest
from click.testing import CliRunner


@pytest.fixture(autouse=True)
def unset_env(monkeypatch):
    monkeypatch.delenv("ANYMOTION_ROOT", raising=False)
    monkeypatch.delenv("ANYMOTION_API_URL", raising=False)
    monkeypatch.delenv("ANYMOTION_CLIENT_ID", raising=False)
    monkeypatch.delenv("ANYMOTION_CLIENT_SECRET", raising=False)
    monkeypatch.setenv("ANYMOTION_USE_SPINNER", "false")
    monkeypatch.setenv("ANYMOTION_STDOUT_ISSHOW", "true")


@pytest.fixture
def runner():
    yield CliRunner()


@pytest.fixture
def make_dir(tmp_path):
    def _make_dir(name):
        (tmp_path / name).mkdir()
        return tmp_path / name

    return _make_dir


@pytest.fixture
def make_file(tmp_path):
    def _make_file(name, content=None):
        if content:
            (tmp_path / name).write_text(content)
        else:
            (tmp_path / name).touch()
        return tmp_path / name

    return _make_file
