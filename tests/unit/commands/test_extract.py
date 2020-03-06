from pathlib import Path
from textwrap import dedent

import pytest
from encore_sdk import RequestsError

from encore_api_cli.commands.extract import cli


class TestExtract(object):
    @pytest.mark.parametrize(
        "args", [["extract", "--movie-id", "111"], ["extract", "--image-id", "111"]],
    )
    @pytest.mark.parametrize(
        "status, expected",
        [
            ("SUCCESS", "Success: Keypoint extraction is complete.",),
            ("TIMEOUT", "Error: Keypoint extraction is timed out.",),
            ("FAILURE", "Error: Keypoint extraction failed.\nmessage",),
        ],
    )
    def test_valid(self, runner, make_client, args, status, expected):
        keypoint_id = 111
        client_mock = make_client(status=status, keypoint_id=keypoint_id)

        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            f"Keypoint extraction started. (keypoint id: {keypoint_id})\n{expected}\n"
        )

    def test_with_spinner(self, monkeypatch, runner, make_client):
        monkeypatch.setenv("ANYMOTION_USE_SPINNER", "true")
        client_mock = make_client()

        result = runner.invoke(cli, ["extract", "--image-id", "111"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert "Processing..." in result.output

    def test_with_drawing(self, runner, make_client):
        path = (Path(".") / "image.jpg").resolve()
        client_mock = make_client(with_drawing=True)

        result = runner.invoke(cli, ["extract", "--image-id", "111", "--with-drawing"])

        assert client_mock.call_count == 2
        assert client_mock.return_value.draw_keypoint.call_count == 1
        assert client_mock.return_value.download.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            f"""\
            Keypoint extraction started. (keypoint id: 111)
            Success: Keypoint extraction is complete.

            Drawing started. (drawing id: 333)
            Success: Drawing is complete.
            Downloaded the file to {path}.
            """
        )

    @pytest.mark.parametrize(
        "with_extract_exception, with_wait_exception", [(True, True), (False, True)]
    )
    def test_with_error(
        self, runner, make_client, with_extract_exception, with_wait_exception
    ):
        client_mock = make_client(
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
    def test_invalid_params(self, runner, make_client, args, expected):
        client_mock = make_client()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert expected in result.output

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(
            status="SUCCESS",
            keypoint_id=111,
            with_extract_exception=False,
            with_wait_exception=False,
            with_drawing=False,
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

            if with_drawing:
                client_mock.return_value.draw_keypoint.return_value = 333
                client_mock.return_value.download.return_value = None

                wait_mock = client_mock.return_value.wait_for_drawing
                wait_mock.return_value.status = "SUCCESS"
                wait_mock.return_value.get.return_value = "http://example.com/image.jpg"

                mocker.patch("encore_api_cli.commands.draw.get_client", client_mock)
                mocker.patch(
                    "encore_api_cli.commands.draw.get_name_from_drawing_id",
                    mocker.MagicMock(return_value="image"),
                )

            mocker.patch("encore_api_cli.commands.extract.get_client", client_mock)
            return client_mock

        return _make_client
