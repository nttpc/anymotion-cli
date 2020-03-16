from pathlib import Path
from textwrap import dedent

import pytest

from encore_api_cli.commands.configure import cli
from encore_api_cli.exceptions import SettingsValueError


@pytest.fixture()
def make_configure_file(mocker, tmp_path):
    def _make_configure_file(config_content="", credentials_content=""):
        mocker.patch("pathlib.Path.home", mocker.MagicMock(return_value=tmp_path))

        settings_dir = tmp_path / ".anymotion"
        settings_dir.mkdir(exist_ok=True)

        config_file = settings_dir / "config"
        config_file.write_text(config_content)

        credentials_file = settings_dir / "credentials"
        credentials_file.write_text(credentials_content)

        return config_file, credentials_file

    return _make_configure_file


class TestConfigure(object):
    @pytest.mark.parametrize(
        "defaults, inputs, expected",
        [
            (
                ["http://api.example.com/anymotion/v1/", None, None],
                ["", "client_id", "client_secret"],
                (
                    "AnyMotion API URL [http://api.example.com/anymotion/v1/]: \n"
                    "AnyMotion Client ID: \n"
                    "AnyMotion Client Secret: \n"
                ),
            ),
            (
                ["http://api.example.com/anymotion/v1/", None, None],
                [
                    "http://dev-api.example.com/anymotion/v1/",
                    "client_id",
                    "client_secret",
                ],
                (
                    "AnyMotion API URL [http://api.example.com/anymotion/v1/]: "
                    "http://dev-api.example.com/anymotion/v1/\n"
                    "AnyMotion Client ID: \n"
                    "AnyMotion Client Secret: \n"
                ),
            ),
            (
                ["http://api.example.com/anymotion/v1/", "client_id", "client_secret"],
                ["", "", ""],
                (
                    "AnyMotion API URL [http://api.example.com/anymotion/v1/]: \n"
                    "AnyMotion Client ID [****************t_id]: \n"
                    "AnyMotion Client Secret [****************cret]: \n"
                ),
            ),
            (
                ["http://api.example.com/anymotion/v1/", "client_id", "client_secret"],
                ["", "client_id2", "client_secre2"],
                (
                    "AnyMotion API URL [http://api.example.com/anymotion/v1/]: \n"
                    "AnyMotion Client ID [****************t_id]: \n"
                    "AnyMotion Client Secret [****************cret]: \n"
                ),
            ),
        ],
    )
    def test_valid(self, mocker, runner, home_mock, defaults, inputs, expected):
        settings_mock = self._get_settings_mock(mocker, defaults)

        result = runner.invoke(cli, ["configure"], input="\n".join(inputs) + "\n")

        assert settings_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    def test_invalid(self, mocker, runner, home_mock):
        api_url = "http://api.example.com/"
        settings_mock = self._get_settings_mock(mocker, with_exception=True)

        result = runner.invoke(
            cli, ["configure"], input=f"{api_url}\nclient id\nclient secret\n"
        )

        assert settings_mock.call_count == 1
        assert result.exit_code == 1
        assert result.output.endswith("Error: api_url is invald.\n")

    @pytest.fixture
    def home_mock(self, mocker, tmpdir):
        tmpdir = Path(tmpdir)
        mocker.patch("pathlib.Path.home", mocker.MagicMock(return_value=tmpdir))

    def _get_settings_mock(
        self,
        mocker,
        defaults=["http://api.example.com/anymotion/v1/", None, None],
        with_exception=False,
    ):
        settings_mock = mocker.MagicMock()

        settings_mock.return_value.api_url = defaults[0]
        settings_mock.return_value.client_id = defaults[1]
        settings_mock.return_value.client_secret = defaults[2]

        write_config_mock = settings_mock.return_value.write_config
        if with_exception:
            write_config_mock.side_effect = SettingsValueError("api_url is invald.")
        else:
            write_config_mock.return_value = None
        settings_mock.return_value.write_credentials.return_value = None

        mocker.patch("encore_api_cli.commands.configure.get_settings", settings_mock)
        return settings_mock


@pytest.mark.parametrize(
    "client_id, expected_client_id",
    [("client_id", "****************t_id"), (None, "None")],
)
def test_configure_list(mocker, runner, client_id, expected_client_id):
    expected = dedent(
        f"""\
        Name              Value
        ----------------  -----------------------
        profile           default
        api_url           https://api.example.jp/
        client_id         {expected_client_id}
        client_secret     ****************cret
        polling_interval  10
        timeout           600
    """
    )

    settings_mock = mocker.MagicMock()
    settings_mock.return_value.api_url = "https://api.example.jp/"
    settings_mock.return_value.client_id = client_id
    settings_mock.return_value.client_secret = "client_secret"
    settings_mock.return_value.interval = 10
    settings_mock.return_value.timeout = 600
    mocker.patch("encore_api_cli.commands.configure.get_settings", settings_mock)

    result = runner.invoke(cli, ["configure", "list"])

    assert result.exit_code == 0
    assert expected in result.output


class TestConfigureGet(object):
    @pytest.mark.parametrize(
        "args, expected, exists",
        [
            (["configure", "get", "client_id"], "client_id\n", True),
            (["configure", "get", "client_secret"], "client_secret\n", True),
            (["configure", "get", "CLIENT_ID"], "client_id\n", True),
            (["configure", "get", "CLIENT_SECRET"], "client_secret\n", True),
            (["configure", "get", "client_id"], "\n", False),
            (["configure", "get", "client_secret"], "\n", False),
            (
                ["configure", "get", "api_url"],
                "https://api.customer.jp/anymotion/v1/\n",
                False,
            ),
            (["configure", "get", "polling_interval"], "5\n", False),
            (["configure", "get", "timeout"], "600\n", False),
            (["configure", "get", "is_download"], "True\n", False),
            (["configure", "get", "is_open"], "False\n", False),
        ],
    )
    def test_valid(self, runner, make_configure_file, args, expected, exists):
        if exists:
            content = dedent(
                """\
                [default]
                anymotion_client_id = client_id
                anymotion_client_secret = client_secret
                """
            )
        else:
            content = ""
        make_configure_file(credentials_content=content)

        result = runner.invoke(cli, args)

        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["configure", "get"], "Error: Missing argument"),
            (["configure", "get", "invalid_value"], "Error: Invalid value"),
        ],
    )
    def test_invalid_params(self, runner, args, expected):
        result = runner.invoke(cli, args)

        assert result.exit_code == 2
        assert expected in result.output


class TestConfigureSet(object):
    @pytest.mark.parametrize(
        "args, expected, content",
        [
            (["configure", "set", "client_id", "client_id"], ("client_id", ""), ""),
            (
                ["configure", "set", "client_secret", "client_secret"],
                ("", "client_secret"),
                "",
            ),
            (["configure", "set", "CLIENT_ID", "client_id"], ("client_id", ""), ""),
            (
                ["configure", "set", "CLIENT_SECRET", "client_secret"],
                ("", "client_secret"),
                "",
            ),
            (
                ["configure", "set", "client_id", "client_id2"],
                ("client_id2", "client_secret"),
                dedent(
                    """\
                    [default]
                    anymotion_client_id = client_id
                    anymotion_client_secret = client_secret

                    """
                ),
            ),
        ],
    )
    def test_valid(self, runner, make_configure_file, args, expected, content):
        _, credentials_file = make_configure_file(credentials_content=content)

        result = runner.invoke(cli, args)

        assert result.exit_code == 0
        assert result.output == ""
        assert credentials_file.read_text() == dedent(
            f"""\
            [default]
            anymotion_client_id = {expected[0]}
            anymotion_client_secret = {expected[1]}

            """
        )

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["configure", "set"],
                (
                    "Error: Missing argument '[client_id|client_secret]'.  "
                    "Choose from:\n\tclient_id,\n\tclient_secret.\n"
                ),
            ),
            (
                ["configure", "set", "invalid_key"],
                (
                    "Error: Invalid value for '[client_id|client_secret]': "
                    "invalid choice: invalid_key. "
                    "(choose from client_id, client_secret)\n"
                ),
            ),
            (["configure", "set", "client_id"], "Error: Missing argument 'VALUE'.\n"),
            (
                ["configure", "set", "client_secret"],
                "Error: Missing argument 'VALUE'.\n",
            ),
        ],
    )
    def test_invalid_params(self, runner, args, expected):
        result = runner.invoke(cli, args)

        assert result.exit_code == 2
        assert result.output.endswith(expected)


class TestConfigureClear(object):
    @pytest.mark.parametrize(
        "content",
        [
            dedent(
                """\
                [default]
                anymotion_api_url = https://api.example.jp/anymotion/v1/

                """
            ),
        ],
    )
    def test_clear_config(self, runner, make_configure_file, content):
        config_file, _ = make_configure_file(config_content=content)

        result = runner.invoke(cli, ["configure", "clear"])

        assert result.exit_code == 0
        assert result.output == ""
        assert config_file.read_text() == dedent(
            """\
            [default]
            anymotion_api_url = https://api.customer.jp/anymotion/v1/

            """
        )

    @pytest.mark.parametrize(
        "content",
        [
            dedent(
                """\
                [default]
                anymotion_client_id = client_id
                anymotion_client_secret = client_secret

                """
            ),
        ],
    )
    def test_clear_credentials(self, runner, make_configure_file, content):
        _, credentials_file = make_configure_file(credentials_content=content)

        result = runner.invoke(cli, ["configure", "clear"])

        assert result.exit_code == 0
        assert result.output == ""
        none = ""
        assert credentials_file.read_text() == dedent(
            f"""\
            [default]
            anymotion_client_id = {none}
            anymotion_client_secret = {none}

            """
        )
