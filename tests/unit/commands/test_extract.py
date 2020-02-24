from textwrap import dedent

import pytest
from encore_sdk import RequestsError

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
    def test_valid(self, mocker, runner, args, status, expected):
        keypoint_id = 111
        client_mock = self._get_client_mock(
            mocker, status=status, keypoint_id=keypoint_id
        )

        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            f"Keypoint extraction started. (keypoint id: {keypoint_id})\n{expected}\n"
        )

    def test_with_spinner(self, mocker, monkeypatch, runner):
        monkeypatch.setenv("ANYMOTION_USE_SPINNER", "true")
        client_mock = self._get_client_mock(mocker)

        result = runner.invoke(cli, ["extract", "--movie-id", "111"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert "Processing..." in result.output

    @pytest.mark.parametrize(
        "with_extract_exception, with_wait_exception", [(True, True), (False, True)]
    )
    def test_with_error(
        self, mocker, runner, with_extract_exception, with_wait_exception
    ):
        client_mock = self._get_client_mock(
            mocker,
            with_extract_exception=with_extract_exception,
            with_wait_exception=with_wait_exception,
        )
        result = runner.invoke(cli, ["extract", "--movie-id", "111"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert "Error" in result.output

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
    def test_invalid_params(self, mocker, runner, args, expected):
        client_mock = self._get_client_mock(mocker)
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert expected in result.output

    def _get_client_mock(
        self,
        mocker,
        status="SUCCESS",
        keypoint_id=111,
        with_extract_exception=False,
        with_wait_exception=False,
    ):
        client_mock = mocker.MagicMock()

        extract_mock = client_mock.return_value.extract_keypoint
        if with_extract_exception:
            extract_mock.side_effect = RequestsError()
        else:
            extract_mock.return_value = keypoint_id

        wait_mock = client_mock.return_value.wait_for_extraction
        if with_wait_exception:
            wait_mock.side_effect = RequestsError()
        else:
            wait_mock.return_value.status = status
            if status == "FAILURE":
                wait_mock.return_value.failure_detail = "message"

        mocker.patch("encore_api_cli.commands.extract.get_client", client_mock)
        return client_mock


# TODO: refactor
def test_keypoint_extract_with_drawing(mocker, runner):
    image_id = 111
    keypoint_id = 222

    client_mock = mocker.MagicMock()
    client_mock.return_value.wait_for_extraction.return_value.status = "SUCCESS"
    client_mock.return_value.extract_keypoint.return_value = keypoint_id
    client_mock.return_value.draw_keypoint.return_value = 333
    wait_mock = client_mock.return_value.wait_for_drawing
    wait_mock.return_value.status = "SUCCESS"
    wait_mock.return_value.get.return_value = "url"
    client_mock.return_value.download.return_value = None
    mocker.patch("encore_api_cli.commands.extract.get_client", client_mock)
    mocker.patch("encore_api_cli.commands.draw.get_client", client_mock)
    mocker.patch(
        "encore_api_cli.commands.draw.get_name_from_drawing_id",
        mocker.MagicMock(return_value="image"),
    )

    result = runner.invoke(cli, ["extract", "--image-id", image_id, "--with-drawing"])

    assert client_mock.call_count == 2
    assert client_mock.return_value.draw_keypoint.call_count == 1
    assert client_mock.return_value.draw_keypoint.call_args == (
        (keypoint_id,),
        {"rule": None},
    )
    assert client_mock.return_value.download.call_count == 1

    assert result.exit_code == 0
