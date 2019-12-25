from click.testing import CliRunner
import textwrap

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


def test_keypoint_extract(mocker):
    client_mock = mocker.MagicMock()
    client_mock.return_value.extract_keypoint.return_value = 2
    mocker.patch('encore_api_cli.commands.keypoint.get_client', client_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ['keypoint', 'extract', '--image_id', '1'])

    assert client_mock.call_count == 1
    assert client_mock.return_value.extract_keypoint.call_count == 1
    assert client_mock.return_value.extract_keypoint.call_args == ({
        'image_id': 1,
        'movie_id': None
    },)

    assert result.exit_code == 0


def test_keypoint_extract_error(mocker):
    runner = CliRunner()
    result = runner.invoke(cli, ['keypoint', 'extract'])

    assert result.exit_code == 2
    assert result.output == textwrap.dedent("""\
        Usage: cli keypoint extract [OPTIONS]

        Error: Either "movie_id" or "image_id" is required.
    """)


def test_keypoint_extract_with_drawing(mocker):
    image_id = 1
    keypoint_id = 2

    client_mock = mocker.MagicMock()
    client_mock.return_value.extract_keypoint.return_value = keypoint_id
    client_mock.return_value.draw_keypoint.return_value = 'url'
    client_mock.return_value.download.return_value = None
    mocker.patch('encore_api_cli.commands.keypoint.get_client', client_mock)

    runner = CliRunner()
    result = runner.invoke(
        cli, ['keypoint', 'extract', '--image_id', image_id, '--with_drawing'])

    assert client_mock.call_count == 1
    assert client_mock.return_value.extract_keypoint.call_count == 1
    assert client_mock.return_value.extract_keypoint.call_args == ({
        'image_id': 1,
        'movie_id': None
    },)
    assert client_mock.return_value.draw_keypoint.call_count == 1
    assert client_mock.return_value.draw_keypoint.call_args == ((keypoint_id,),)
    assert client_mock.return_value.download.call_count == 1

    assert result.exit_code == 0
