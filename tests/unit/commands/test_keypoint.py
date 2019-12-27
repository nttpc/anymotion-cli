from textwrap import dedent

from click.testing import CliRunner
import pytest

from encore_api_cli.client import Client
from encore_api_cli.commands.keypoint import cli

base_url = "http://api.example.com"
api_url = "http://api.example.com/anymotion/v1/"
oauth_url = "http://api.example.com/v1/oauth/accesstokens"


def test_keypoint():
    runner = CliRunner()
    result = runner.invoke(cli, ["keypoint"])

    assert result.exit_code == 0


def test_keypoint_list(mocker, requests_mock):
    client_mock = mocker.MagicMock(
        return_value=Client("client_id", "client_secret", base_url)
    )
    mocker.patch("encore_api_cli.commands.keypoint.get_client", client_mock)

    requests_mock.post(oauth_url, json={"accessToken": "token"})
    requests_mock.get(f"{api_url}keypoints/", json={"data": "", "next": None})

    runner = CliRunner()
    result = runner.invoke(cli, ["keypoint", "list"])

    assert client_mock.call_count == 1

    assert result.exit_code == 0
    assert result.output == "[]\n"


def test_keypoint_extract_movie(mocker):
    movie_id = 111
    keypoint_id = 222

    client_mock = mocker.MagicMock()
    client_mock.return_value.wait_for_extraction.return_value = "SUCCESS"
    extract_keypoint_mock = client_mock.return_value.extract_keypoint_from_movie
    extract_keypoint_mock.return_value = keypoint_id
    mocker.patch("encore_api_cli.commands.keypoint.get_client", client_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ["keypoint", "extract", "--movie_id", movie_id])

    assert client_mock.call_count == 1
    assert extract_keypoint_mock.call_count == 1
    assert extract_keypoint_mock.call_args == ((movie_id,),)

    assert result.exit_code == 0


def test_keypoint_extract_image(mocker):
    image_id = 111
    keypoint_id = 222

    client_mock = mocker.MagicMock()
    client_mock.return_value.wait_for_extraction.return_value = "SUCCESS"
    extract_keypoint_mock = client_mock.return_value.extract_keypoint_from_image
    extract_keypoint_mock.return_value = keypoint_id
    mocker.patch("encore_api_cli.commands.keypoint.get_client", client_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ["keypoint", "extract", "--image_id", image_id])

    assert client_mock.call_count == 1
    assert extract_keypoint_mock.call_count == 1
    assert extract_keypoint_mock.call_args == ((image_id,),)

    assert result.exit_code == 0


def test_keypoint_extract_with_drawing(mocker):
    image_id = 111
    keypoint_id = 222

    client_mock = mocker.MagicMock()
    client_mock.return_value.wait_for_extraction.return_value = "SUCCESS"
    extract_keypoint_mock = client_mock.return_value.extract_keypoint_from_image
    extract_keypoint_mock.return_value = keypoint_id
    client_mock.return_value.draw_keypoint.return_value = "url"
    client_mock.return_value.download.return_value = None
    mocker.patch("encore_api_cli.commands.keypoint.get_client", client_mock)
    mocker.patch("encore_api_cli.commands.draw.get_client", client_mock)

    runner = CliRunner()
    result = runner.invoke(
        cli, ["keypoint", "extract", "--image_id", image_id, "--with_drawing"]
    )

    assert client_mock.call_count == 2
    assert extract_keypoint_mock.call_count == 1
    assert extract_keypoint_mock.call_args == ((image_id,),)
    assert client_mock.return_value.draw_keypoint.call_count == 1
    assert client_mock.return_value.draw_keypoint.call_args == ((keypoint_id,),)
    assert client_mock.return_value.download.call_count == 1

    assert result.exit_code == 0


@pytest.mark.parametrize("options", [[]])
def test_keypoint_extract_error(options):
    runner = CliRunner()
    result = runner.invoke(cli, ["keypoint", "extract"] + options)

    assert result.exit_code == 2
    assert result.output == dedent(
        """\
        Usage: cli keypoint extract [OPTIONS]

        Error: Either "movie_id" or "image_id" is required.
    """
    )
