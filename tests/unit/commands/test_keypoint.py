from click.testing import CliRunner

from encore_api_cli.client import Client
from encore_api_cli.commands.keypoint import cli

base_url = 'http://api.example.com'
api_url = 'http://api.example.com/anymotion/v1/'
oauth_url = 'http://api.example.com/v1/oauth/accesstokens'


def test_keypoint():
    runner = CliRunner()
    result = runner.invoke(cli, ['keypoint'])

    assert result.exit_code == 0


def test_keypoint_list(mocker, requests_mock):
    client_mock = mocker.MagicMock(
        return_value=Client('client_id', 'client_secret', base_url))
    mocker.patch('encore_api_cli.commands.keypoint.get_client', client_mock)

    requests_mock.post(oauth_url, json={'accessToken': 'token'})
    requests_mock.get(f'{api_url}keypoints/', json={'data': '', 'next': None})

    runner = CliRunner()
    result = runner.invoke(cli, ['keypoint', 'list'])

    assert client_mock.call_count == 1

    assert result.exit_code == 0
    assert result.output == '[]\n'
