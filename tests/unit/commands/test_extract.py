from textwrap import dedent

import pytest
from anymotion_sdk import RequestsError

from anymotion_cli.commands.extract import cli


class TestExtract(object):
    @pytest.mark.parametrize(
        "args, use_path",
        [
            (["extract", "--movie-id", "111"], False),
            (["extract", "--image-id", "111"], False),
            (["extract", "--path", "<path>"], True),
        ],
    )
    @pytest.mark.parametrize(
        "status, exit_code, message",
        [
            (
                "SUCCESS",
                0,
                "Success: Keypoint extraction is complete.",
            ),
            (
                "TIMEOUT",
                1,
                "Error: Keypoint extraction is timed out.",
            ),
            (
                "FAILURE",
                1,
                "Error: Keypoint extraction failed.\nmessage",
            ),
        ],
    )
    def test_valid(
        self, runner, make_path, make_client, args, use_path, status, exit_code, message
    ):
        keypoint_id = 111
        expected = (
            f"Keypoint extraction started. (keypoint id: {keypoint_id})\n{message}\n"
        )

        if use_path:
            path = make_path("image.jpg", is_file=True)
            args = [arg.replace("<path>", str(path)) for arg in args]
            expected = "\n" + expected

        client_mock = make_client(
            status=status, keypoint_id=keypoint_id, with_upload=use_path
        )

        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == exit_code
        assert result.output == expected

    def test_with_spinner(self, monkeypatch, runner, make_client):
        monkeypatch.setenv("ANYMOTION_USE_SPINNER", "true")
        client_mock = make_client()

        result = runner.invoke(cli, ["extract", "--image-id", "111"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert "Processing..." in result.output

    def test_with_drawing(self, runner, make_client):
        client_mock = make_client(with_drawing=True)

        result = runner.invoke(cli, ["extract", "--image-id", "111", "--with-drawing"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            """\
            Keypoint extraction started. (keypoint id: 111)
            Success: Keypoint extraction is complete.

            """
        )

    @pytest.mark.parametrize(
        "with_extract_exception, with_wait_exception", [(True, True), (False, True)]
    )
    def test_with_requests_error(
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
        "args, use_path, expected",
        [
            (
                ["extract"],
                False,
                "Error: Either '--image-id' or '--movie-id' or '--path' is required\n",
            ),
            (
                ["extract", "--image-id", "1", "--movie-id", "1"],
                False,
                "Error: Either '--image-id' or '--movie-id' or '--path' is required\n",
            ),
            (
                ["extract", "--image-id", "1", "--path", "<path>"],
                True,
                "Error: Either '--image-id' or '--movie-id' or '--path' is required\n",
            ),
            (
                ["extract", "--movie-id", "1", "--path", "<path>"],
                True,
                "Error: Either '--image-id' or '--movie-id' or '--path' is required\n",
            ),
            (
                ["extract", "--image-id", "1", "--movie-id", "1", "--path", "<path>"],
                True,
                "Error: Either '--image-id' or '--movie-id' or '--path' is required\n",
            ),
            (
                ["extract", "--image-id"],
                False,
                "Error: --image-id option requires an argument\n",
            ),
            (
                ["extract", "--movie-id"],
                False,
                "Error: --movie-id option requires an argument\n",
            ),
            (
                ["extract", "--path"],
                True,
                "Error: --path option requires an argument\n",
            ),
            (
                ["extract", "--movie-id", "invalid_id"],
                False,
                (
                    "Error: Invalid value for '--movie-id': "
                    "invalid_id is not a valid integer\n"
                ),
            ),
            (
                ["extract", "--image-id", "invalid_id"],
                False,
                (
                    "Error: Invalid value for '--image-id': "
                    "invalid_id is not a valid integer\n"
                ),
            ),
            (
                ["extract", "--path", "not_exist"],
                False,
                (
                    "Error: Invalid value for '--path': "
                    "File 'not_exist' does not exist.\n"
                ),
            ),
        ],
    )
    def test_invalid_params(
        self, runner, make_path, make_client, args, use_path, expected
    ):
        keypoint_id = 111

        if use_path:
            path = make_path("image.jpg", is_file=True)
            args = [arg.replace("<path>", str(path)) for arg in args]

        client_mock = make_client(keypoint_id=keypoint_id, with_upload=True)

        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert result.output.endswith(expected)

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(
            status="SUCCESS",
            keypoint_id=111,
            with_extract_exception=False,
            with_wait_exception=False,
            with_drawing=False,
            with_upload=False,
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
                mocker.patch("anymotion_cli.commands.extract.draw", mocker.MagicMock())

            if with_upload:
                mocker.patch(
                    "anymotion_cli.commands.extract.upload", mocker.MagicMock()
                )

            mocker.patch("anymotion_cli.commands.extract.get_client", client_mock)
            return client_mock

        return _make_client
