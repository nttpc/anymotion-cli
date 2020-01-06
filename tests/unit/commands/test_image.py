from textwrap import dedent

from click.testing import CliRunner

from encore_api_cli.client import Client
from encore_api_cli.commands.image import cli

base_url = "http://api.example.com"
api_url = "http://api.example.com/anymotion/v1/"
oauth_url = "http://api.example.com/v1/oauth/accesstokens"


def test_image():
    runner = CliRunner()
    result = runner.invoke(cli, ["image"])

    assert result.exit_code == 0


def test_image_list(mocker, requests_mock):
    expected = dedent(
        """\
            [
              {
                "id": 1,
                "name": null
              }
            ]

        """
    )
    client_mock = mocker.MagicMock(
        return_value=Client("client_id", "client_secret", base_url, 5, 600)
    )
    mocker.patch("encore_api_cli.commands.image.get_client", client_mock)

    requests_mock.post(oauth_url, json={"accessToken": "token"})
    requests_mock.get(
        f"{api_url}images/", json={"data": [{"id": 1, "name": None}], "next": None}
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["image", "list"])

    assert client_mock.call_count == 1

    assert result.exit_code == 0
    assert result.output == expected
