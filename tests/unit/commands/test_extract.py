from textwrap import dedent

import pytest
from click.testing import CliRunner

from encore_api_cli.commands.extract import cli


class TestExtract(object):
    @pytest.mark.parametrize(
        "args, status, expected",
        [
            (
                ["extract", "--movie_id", "111"],
                "SUCCESS",
                "Success: Keypoint extraction is complete.",
            ),
            (
                ["extract", "--image_id", "111"],
                "SUCCESS",
                "Success: Keypoint extraction is complete.",
            ),
            (
                ["extract", "--movie_id", "111"],
                "TIMEOUT",
                "Keypoint extraction is timed out.",
            ),
            (
                ["extract", "--image_id", "111"],
                "TIMEOUT",
                "Keypoint extraction is timed out.",
            ),
            (
                ["extract", "--movie_id", "111"],
                "FAILURE",
                "Keypoint extraction failed.",
            ),
            (
                ["extract", "--image_id", "111"],
                "FAILURE",
                "Keypoint extraction failed.",
            ),
        ],
    )
    def test_valid(self, mocker, args, status, expected):
        keypoint_id = 111
        client_mock = self._get_client_mock(
            mocker, status=status, keypoint_id=keypoint_id
        )

        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            f"""\
                Keypoint extraction started. (keypoint_id: {keypoint_id})
                {expected}
            """
        )

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["extract"], 'Error: Either "movie_id" or "image_id" is required',),
            (
                ["extract", "--image_id", "1", "--movie_id", "1"],
                'Error: Either "movie_id" or "image_id" is required',
            ),
            (
                ["extract", "--image_id"],
                "Error: --image_id option requires an argument",
            ),
            (
                ["extract", "--movie_id"],
                "Error: --movie_id option requires an argument",
            ),
            (
                ["extract", "--movie_id", "invalid_id"],
                'Error: Invalid value for "--movie_id"',
            ),
            (
                ["extract", "--image_id", "invalid_id"],
                'Error: Invalid value for "--image_id"',
            ),
        ],
    )
    def test_invalid_params(self, mocker, args, expected):
        client_mock = self._get_client_mock(mocker)
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert expected in result.output

    def _get_client_mock(self, mocker, status="SUCCESS", keypoint_id=111):
        client_mock = mocker.MagicMock()
        client_mock.return_value.wait_for_extraction.return_value = status
        client_mock.return_value.extract_keypoint_from_movie.return_value = keypoint_id
        client_mock.return_value.extract_keypoint_from_image.return_value = keypoint_id
        mocker.patch("encore_api_cli.commands.extract.get_client", client_mock)
        return client_mock


# TODO: refactor
def test_keypoint_extract_with_drawing(mocker):
    image_id = 111
    keypoint_id = 222

    client_mock = mocker.MagicMock()
    client_mock.return_value.wait_for_extraction.return_value = "SUCCESS"
    extract_keypoint_mock = client_mock.return_value.extract_keypoint_from_image
    extract_keypoint_mock.return_value = keypoint_id
    client_mock.return_value.draw_keypoint.return_value = 333
    client_mock.return_value.wait_for_drawing.return_value = ("SUCCESS", "url")
    client_mock.return_value.download.return_value = None
    mocker.patch("encore_api_cli.commands.extract.get_client", client_mock)
    mocker.patch("encore_api_cli.commands.draw.get_client", client_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ["extract", "--image_id", image_id, "--with_drawing"])

    assert client_mock.call_count == 2
    assert extract_keypoint_mock.call_count == 1
    assert extract_keypoint_mock.call_args == ((image_id,),)
    assert client_mock.return_value.draw_keypoint.call_count == 1
    assert client_mock.return_value.draw_keypoint.call_args == (
        (keypoint_id,),
        {"rule": None},
    )
    assert client_mock.return_value.download.call_count == 1

    assert result.exit_code == 0
