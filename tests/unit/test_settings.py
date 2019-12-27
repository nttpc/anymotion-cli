from pathlib import Path
from textwrap import dedent

import pytest

from encore_api_cli.exceptions import SettingsValueError
from encore_api_cli.settings import Settings


@pytest.fixture
def mocker_home(mocker, tmpdir):
    tmpdir = Path(tmpdir)
    mocker.patch("pathlib.Path.home", mocker.MagicMock(return_value=tmpdir))
    yield tmpdir


@pytest.fixture
def set_env(monkeypatch):
    monkeypatch.setenv("ANYMOTION_CLIENT_ID", "client_id_from_env")
    monkeypatch.setenv("ANYMOTION_CLIENT_SECRET", "client_secret_from_env")


@pytest.fixture
def credentials_file(mocker_home):
    credentials_file_path = mocker_home / ".anymotion" / "credentials"
    (mocker_home / ".anymotion").mkdir()
    credentials_file_path.write_text(
        dedent(
            """\
                [default]
                anymotion_client_id = client_id_from_file
                anymotion_client_secret = client_secret_from_file
            """
        )
    )


class Test_設定ファイルが存在しない場合(object):
    def test_設定情報の初期値を取得できること(self, mocker_home):
        settings = Settings("default")

        assert settings.interval == 5
        assert settings.timeout == 600
        assert settings.url == "https://api.customer.jp/"
        assert settings.client_id is None
        assert settings.client_secret is None

    def test_デフォルト値と等しい場合configファイルを作成しないこと(self, mocker_home):
        config_file_path = mocker_home / ".anymotion" / "config"

        assert not config_file_path.exists()

        settings = Settings("default")
        settings.write_config()

        assert not config_file_path.exists()

    def test_デフォルト値と等しくない場合configファイルを作成できること(self, mocker_home):
        config_file_path = mocker_home / ".anymotion" / "config"

        assert not config_file_path.exists()

        settings = Settings("default")
        settings.url = "http://api.example.com/"
        settings.write_config()

        assert config_file_path.exists()

    def test_credentialsファイルを作成できること(self, mocker_home):
        credentials_file_path = mocker_home / ".anymotion" / "credentials"

        assert not credentials_file_path.exists()

        settings = Settings("default")
        settings.client_id = "client_id"
        settings.client_secret = "client_secret"
        settings.write_credentials()

        assert credentials_file_path.exists()

    def test_configファイルを更新できること(self, mocker_home):
        settings1 = Settings("default")
        settings1.url = "http://api.example.com/"
        settings1.write_config()

        settings2 = Settings("default")

        assert settings2.url == "http://api.example.com/"

    def test_credentialsファイルを更新できること(self, mocker_home):
        settings1 = Settings("default")
        settings1.client_id = "client_id"
        settings1.client_secret = "client_secret"
        settings1.write_credentials()

        settings2 = Settings("default")

        assert settings2.client_id == "client_id"
        assert settings2.client_secret == "client_secret"

    def test_正しい値出ない場合credentialsファイルを更新できないこと(self, mocker_home):
        settings = Settings("default")
        with pytest.raises(ValueError):
            settings.write_credentials()


class Test_設定ファイルが存在する場合(object):
    def test_configファイルの値が設定されていること(self, mocker_home):
        config_file_path = mocker_home / ".anymotion" / "config"
        (mocker_home / ".anymotion").mkdir()
        config_file_path.write_text(
            dedent(
                """\
                [default]
                anymotion_api_url = http://api.example.com/
                polling_interval = 20
                timeout = 300
            """
            )
        )

        settings = Settings("default")

        assert settings.url == "http://api.example.com/"
        assert settings.interval == 20
        assert settings.timeout == 300

    @pytest.mark.parametrize("interval, timeout", [(0, 10), ("a", 10), (10, -1)])
    def test_configファイルの値が無効な場合エラーが発生すること(self, mocker_home, interval, timeout):
        config_file_path = mocker_home / ".anymotion" / "config"
        (mocker_home / ".anymotion").mkdir()
        config_file_path.write_text(
            dedent(
                f"""\
                [default]
                anymotion_api_url = http://api.example.com/
                polling_interval = {interval}
                timeout = {timeout}
            """
            )
        )

        with pytest.raises(SettingsValueError):
            Settings("default")

    def test_credentialsファイルの値が設定されていること(self, mocker_home, credentials_file):
        settings = Settings("default")

        assert settings.client_id == "client_id_from_file"
        assert settings.client_secret == "client_secret_from_file"


class Test_環境変数が存在する場合(object):
    def test_環境変数の値が設定されていること(self, mocker_home, set_env):
        settings = Settings("default")

        assert settings.client_id == "client_id_from_env"
        assert settings.client_secret == "client_secret_from_env"

    def test_環境変数の値が設定されていないこと(self, mocker_home, set_env):
        settings = Settings("default", use_env=False)

        assert settings.client_id is None
        assert settings.client_secret is None


class Test_設定ファイルと環境変数の両方が存在する場合(object):
    def test_環境変数の値が設定されていること(self, mocker_home, credentials_file, set_env):
        settings = Settings("default")

        assert settings.client_id == "client_id_from_env"
        assert settings.client_secret == "client_secret_from_env"
