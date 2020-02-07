from textwrap import dedent

import pytest
from click.testing import CliRunner

from encore_api_cli.commands.extract import cli


class TestExtract(object):
    @pytest.mark.parametrize(
        "args, status, expected",
        [
            (
                ["extract", "--movie-id", "111"],
                "SUCCESS",
                "Success: Keypoint extraction is complete.",
            ),
            (
                ["extract", "--image-id", "111"],
                "SUCCESS",
                "Success: Keypoint extraction is complete.",
            ),
            (
                ["extract", "--movie-id", "111"],
                "TIMEOUT",
                "Error: Keypoint extraction is timed out.",
            ),
            (
                ["extract", "--image-id", "111"],
                "TIMEOUT",
                "Error: Keypoint extraction is timed out.",
            ),
            (
                ["extract", "--movie-id", "111"],
                "FAILURE",
                "Error: Keypoint extraction failed.\nmessage",
            ),
            (
                ["extract", "--image-id", "111"],
                "FAILURE",
                "Error: Keypoint extraction failed.\nmessage",
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
        assert result.output == (
            f"Keypoint extraction started. (keypoint id: {keypoint_id})\n{expected}\n"
        )

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["extract"], 'Error: Either "--movie-id" or "--image-id" is required',),
            (
                ["extract", "--image-id", "1", "--movie-id", "1"],
                'Error: Either "--movie-id" or "--image-id" is required',
            ),
            (
                ["extract", "--image-id"],
                "Error: --image-id option requires an argument",
            ),
            (
                ["extract", "--movie-id"],
                "Error: --movie-id option requires an argument",
            ),
            (
                ["extract", "--movie-id", "invalid_id"],
                'Error: Invalid value for "--movie-id"',
            ),
            (
                ["extract", "--image-id", "invalid_id"],
                'Error: Invalid value for "--image-id"',
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
        client_mock.return_value.wait_for_extraction.return_value.status = status
        client_mock.return_value.wait_for_extraction.return_value.failure_detail = (
            "message"
        )
        client_mock.return_value.extract_keypoint_from_movie.return_value = keypoint_id
        client_mock.return_value.extract_keypoint_from_image.return_value = keypoint_id
        mocker.patch("encore_api_cli.commands.extract.get_client", client_mock)
        return client_mock


# TODO: refactor
def test_keypoint_extract_with_drawing(mocker):
    image_id = 111
    keypoint_id = 222

    client_mock = mocker.MagicMock()
    client_mock.return_value.wait_for_extraction.return_value.status = "SUCCESS"
    extract_keypoint_mock = client_mock.return_value.extract_keypoint_from_image
    extract_keypoint_mock.return_value = keypoint_id
    client_mock.return_value.draw_keypoint.return_value = 333
    client_mock.return_value.wait_for_drawing.return_value = ("SUCCESS", "url")
    client_mock.return_value.download.return_value = None
    mocker.patch("encore_api_cli.commands.extract.get_client", client_mock)
    mocker.patch("encore_api_cli.commands.draw.get_client", client_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ["extract", "--image-id", image_id, "--with-drawing"])

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
