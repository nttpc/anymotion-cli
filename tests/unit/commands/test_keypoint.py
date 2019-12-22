from click.testing import CliRunner

from encore_api_cli.client import Client
from encore_api_cli.commands.keypoint import cli

base_url = 'http://api.example.com'


def test_keypoint():
    runner = CliRunner()
    result = runner.invoke(cli, ['keypoint'])

    assert result.exit_code == 0


def test_keypoint_list(mocker, requests_mock):
    client_mock = mocker.MagicMock(return_value=Client('token', base_url))
    mocker.patch('encore_api_cli.commands.keypoint.get_client', client_mock)

    requests_mock.get(f'{base_url}/keypoints/',
                      json={
                          'data': '',
                          'next': None
                      })

    runner = CliRunner()
    result = runner.invoke(cli, ['keypoint', 'list'])

    assert result.exit_code == 0
    assert result.output == '[]\n'
