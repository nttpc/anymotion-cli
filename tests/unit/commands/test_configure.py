from pathlib import Path
from textwrap import dedent

import pytest

from encore_api_cli.commands.configure import cli
from encore_api_cli.exceptions import SettingsValueError


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


def test_configure_clear(mocker, tmpdir, runner):
    tmpdir = Path(tmpdir)
    mocker.patch("pathlib.Path.home", mocker.MagicMock(return_value=tmpdir))

    settings_dir = tmpdir / ".anymotion"
    settings_dir.mkdir(exist_ok=True)

    config_file = settings_dir / "config"
    config_file.write_text(
        dedent(
            """\
            [default]
            anymotion_api_url = https://api.example.jp/anymotion/v1/

            """
        )
    )

    result = runner.invoke(cli, ["configure", "clear"])

    assert result.exit_code == 0
    assert result.output == ""

    config = config_file.read_text()
    assert config == dedent(
        """\
        [default]
        anymotion_api_url = https://api.customer.jp/anymotion/v1/

        """
    )
