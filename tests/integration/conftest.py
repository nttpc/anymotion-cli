from textwrap import dedent

import pytest
from click.testing import CliRunner


@pytest.fixture(autouse=True)
def configure(monkeypatch, tmp_path):
    (tmp_path / ".anymotion").mkdir()
    (tmp_path / ".anymotion" / "config").write_text(
        dedent(
            """\
            [default]
            anymotion_api_url = http://api.example.com/anymotion/v1/
            """
        )
    )
    (tmp_path / ".anymotion" / "credentials").write_text(
        dedent(
            """\
            [default]
            anymotion_client_secret = client_secret
            anymotion_client_id = client_id
            """
        )
    )

    monkeypatch.setenv("ANYMOTION_ROOT", str(tmp_path))
    monkeypatch.delenv("ANYMOTION_API_URL", raising=False)
    monkeypatch.delenv("ANYMOTION_CLIENT_ID", raising=False)
    monkeypatch.delenv("ANYMOTION_CLIENT_SECRET", raising=False)
    monkeypatch.setenv("ANYMOTION_USE_SPINNER", "false")
    monkeypatch.setenv("ANYMOTION_STDOUT_ISSHOW", "true")


@pytest.fixture(autouse=True)
def set_requests_mock(requests_mock):
    oauth_url = "http://api.example.com/v1/oauth/accesstokens"
    requests_mock.post(oauth_url, json={"accessToken": "token"})


@pytest.fixture
def runner():
    yield CliRunner()


@pytest.fixture
def image_path(tmp_path):
    path = tmp_path / "image.jpg"
    path.touch()
    yield path
