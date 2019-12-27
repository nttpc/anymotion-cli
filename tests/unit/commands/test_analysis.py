from click.testing import CliRunner

from encore_api_cli.client import Client
from encore_api_cli.commands.analysis import cli

base_url = "http://api.example.com/"
api_url = "http://api.example.com/anymotion/v1/"
oauth_url = "http://api.example.com/v1/oauth/accesstokens"


def test_analysis():
    runner = CliRunner()
    result = runner.invoke(cli, ["analysis"])

    assert result.exit_code == 0


def test_analysis_list(mocker, requests_mock):
    client_mock = mocker.MagicMock(
        return_value=Client("client_id", "client_secret", base_url, 5, 600)
    )
    mocker.patch("encore_api_cli.commands.analysis.get_client", client_mock)

    requests_mock.post(oauth_url, json={"accessToken": "token"})
    requests_mock.get(f"{api_url}analyses/", json={"data": "", "next": None})

    runner = CliRunner()
    result = runner.invoke(cli, ["analysis", "list"])

    assert client_mock.call_count == 1

    assert result.exit_code == 0
    assert result.output == "[]\n"
