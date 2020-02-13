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
def make_path(tmp_path):
    """Make temporary path.

    Examples:
        >>> path = make_path("image.jpg", is_file=True)
        >>> path
        PosixPath('/tmp/pytest-xxx/test_xxx/image.jpg')
    """

    def _make_path(name, exists=True, is_file=False, is_dir=False, content=None):
        if not (is_file ^ is_dir):
            raise Exception("Either is_file or is_dir must be True.")

        path = tmp_path / name

        if is_file and exists:
            if content:
                path.write_text(content)
            else:
                path.touch()
        elif is_dir and exists:
            path.mkdir()

        return path

    return _make_path


# TODO: use make_path
@pytest.fixture
def make_dir(tmp_path):
    def _make_dir(name):
        (tmp_path / name).mkdir()
        return tmp_path / name

    return _make_dir


# TODO: use make_path
@pytest.fixture
def make_file(tmp_path):
    def _make_file(name, content=None):
        if content:
            (tmp_path / name).write_text(content)
        else:
            (tmp_path / name).touch()
        return tmp_path / name

    return _make_file
