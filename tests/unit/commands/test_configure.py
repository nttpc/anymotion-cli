from pathlib import Path
from textwrap import dedent

import pytest
from click.testing import CliRunner

from encore_api_cli.commands.configure import cli


def test_configure(mocker, tmpdir):
    default_url = "https://api.customer.jp/anymotion/v1/"
    api_url = "http://api.example.com/anymotion/v1/"
    expected = dedent(
        f"""\
        AnyMotion API URL [{default_url}]: {api_url}
        AnyMotion Client ID: client id
        AnyMotion Client Secret: client secret
    """
    )

    tmpdir = Path(tmpdir)
    mocker.patch("pathlib.Path.home", mocker.MagicMock(return_value=tmpdir))

    runner = CliRunner()
    result = runner.invoke(
        cli, ["configure"], input=f"{api_url}\nclient id\nclient secret\n"
    )

    assert not result.exception
    assert result.output == expected


@pytest.mark.parametrize(
    "client_id, expected_client_id",
    [("client_id", "****************t_id"), (None, "None")],
)
def test_configure_list(mocker, client_id, expected_client_id):
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

    runner = CliRunner()
    result = runner.invoke(cli, ["configure", "list"])

    assert result.exit_code == 0
    assert expected in result.output
