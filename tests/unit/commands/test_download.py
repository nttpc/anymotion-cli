import io
from pathlib import Path
from textwrap import dedent

import pytest
from anymotion_sdk import RequestsError

from anymotion_cli.commands.download import _get_name_from_keypoint_id, _is_skip, cli


class TestDownload(object):
    @pytest.mark.parametrize(
        "args, status, expected",
        [
            (
                ["download", "111"],
                "SUCCESS",
                "Downloaded the file to {path}.\nOpen the Downloaded file? [y/N]: \n",
            ),
            (
                ["download", "111", "-o", "."],
                "SUCCESS",
                "Downloaded the file to {path}.\nOpen the Downloaded file? [y/N]: \n",
            ),
            (
                ["download", "111", "--out", "."],
                "SUCCESS",
                "Downloaded the file to {path}.\nOpen the Downloaded file? [y/N]: \n",
            ),
            (
                ["download", "-o", ".", "111"],
                "SUCCESS",
                "Downloaded the file to {path}.\nOpen the Downloaded file? [y/N]: \n",
            ),
        ],
    )
    def test_valid(self, runner, make_client, args, status, expected):
        path = (Path(".") / "image.jpg").resolve()
        expected = expected.format(path=path)
        client_mock = make_client(status)

        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.parametrize(
        "input, expected_suffix",
        [("y", ".jpg"), ("Y", ".jpg"), ("n", ".png"), ("N", ".png"), ("", ".png")],
    )
    def test_invalid_suffix(
        self, runner, make_path, make_client, input, expected_suffix
    ):
        path = make_path("image.png", exists=False)
        expected = dedent(
            f"""\
            Warning: ".png" is not a valid extension.
            Change output path from "image.png" to "image.jpg"? [y/N]: {input}
            Downloaded the file to {path.with_suffix(expected_suffix)}.
            Open the Downloaded file? [y/N]: {""}
            """
        )
        client_mock = make_client()

        result = runner.invoke(
            cli, ["download", "111", "-o", str(path)], input=f"{input}\n"
        )

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    def test_with_spinner(self, monkeypatch, runner, make_client):
        monkeypatch.setenv("ANYMOTION_USE_SPINNER", "true")
        client_mock = make_client()

        result = runner.invoke(cli, ["download", "111"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert "Downloading..." in result.output

    @pytest.mark.parametrize(
        "force, is_skip, expected",
        [
            (True, True, "Downloaded the file to {path}."),
            (True, False, "Downloaded the file to {path}."),
            (False, True, "Skip download. To download it, run the following command."),
            (False, False, "Downloaded the file to {path}."),
        ],
    )
    def test_with_exists(self, mocker, runner, make_client, force, is_skip, expected):
        client_mock = make_client()

        path = (Path(".") / "image.jpg").resolve()
        expected = expected.format(path=path)

        args = ["download", "111"]
        if force:
            args += ["--force"]

        mocker.patch(
            "anymotion_cli.commands.download._is_skip",
            mocker.MagicMock(return_value=is_skip),
        )

        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output.startswith(expected)

    @pytest.mark.parametrize("status", ["FAILURE", "TIMEOUT"])
    def test_with_response_error(self, runner, make_client, status):
        client_mock = make_client(status)

        result = runner.invoke(cli, ["download", "111"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert result.output == "Error: Unable to download because drawing failed.\n"

    @pytest.mark.parametrize(
        "with_get_drawing_exception, with_get_name_exception, with_download_exception",
        [(True, True, True), (False, True, True), (False, False, True)],
    )
    def test_with_requests_error(
        self,
        runner,
        make_client,
        with_get_drawing_exception,
        with_get_name_exception,
        with_download_exception,
    ):
        client_mock = make_client(
            with_get_drawing_exception=with_get_drawing_exception,
            with_get_name_exception=with_get_name_exception,
            with_download_exception=with_download_exception,
        )
        result = runner.invoke(cli, ["download", "111"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert "Error" in result.output

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["download"], "Error: Missing argument 'DRAWING_ID'.\n"),
            (
                ["download", "invalid_id"],
                (
                    "Error: Invalid value for 'DRAWING_ID': "
                    "invalid_id is not a valid integer\n",
                ),
            ),
            (["download", "111", "-o"], "Error: -o option requires an argument\n"),
            (["download", "--out"], "Error: --out option requires an argument\n",),
            (
                ["download", "111", "-o", "not_exist_dir/file_name"],
                (
                    "Error: Invalid value for '-o' / '--out': "
                    'File "not_exist_dir/file_name" is not writable.\n'
                ),
            ),
        ],
    )
    def test_invalid_params(self, runner, make_client, args, expected):
        client_mock = make_client()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert result.output.endswith(expected)

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(
            status="SUCCESS",
            with_get_drawing_exception=False,
            with_get_name_exception=False,
            with_download_exception=False,
        ):
            if status == "SUCCESS":
                url = "http://example.com/image.jpg"
            else:
                url = None

            client_mock = mocker.MagicMock()

            get_drawing_mock = client_mock.return_value.get_drawing
            if with_get_drawing_exception:
                get_drawing_mock.side_effect = RequestsError()
            else:
                get_drawing_mock.return_value = {
                    "execStatus": status,
                    "drawingUrl": url,
                    "keypoint": 222,
                }

            if with_download_exception:
                client_mock.return_value.download.side_effect = RequestsError()
            else:
                client_mock.return_value.download.return_value = None

            mocker.patch("anymotion_cli.commands.download.get_client", client_mock)

            if with_get_name_exception:
                get_name_mock = mocker.MagicMock(side_effect=RequestsError())
            else:
                get_name_mock = mocker.MagicMock(return_value="image")
            mocker.patch(
                "anymotion_cli.commands.download._get_name_from_keypoint_id",
                get_name_mock,
            )

            return client_mock

        return _make_client


class TestGetNameFromKeypointId(object):
    @pytest.mark.parametrize(
        "media_type, expected", [("image", "image"), ("movie", "movie"), ("None", "")],
    )
    def test_valid(self, make_client, media_type, expected):
        client_mock = make_client(media_type=media_type)
        name = _get_name_from_keypoint_id(client_mock(), 222)

        assert name == expected

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(media_type=None):
            client_mock = mocker.MagicMock()

            if media_type == "image":
                data = {"image": 111, "movie": None}
                client_mock.return_value.get_image.return_value = {"name": "image"}
            elif media_type == "movie":
                data = {"image": None, "movie": 111}
                client_mock.return_value.get_movie.return_value = {"name": "movie"}
            else:
                data = {"image": None, "movie": None}

            client_mock.return_value.get_keypoint.return_value = data

            return client_mock

        return _make_client


class TestIsSkip(object):
    def test_not_exists(self, capfd, make_path):
        path = make_path("image.jpg", exists=False)

        assert _is_skip(path) is False

        out, err = capfd.readouterr()
        assert out == ""
        assert err == ""

    @pytest.mark.parametrize(
        "input, expected",
        [("y", False), ("Y", False), ("n", True), ("N", True), ("\n", True)],
    )
    def test_exists(self, capfd, monkeypatch, make_path, input, expected):
        monkeypatch.setattr("sys.stdin", io.StringIO(input))
        path = make_path("image.jpg", is_file=True)

        assert _is_skip(path) is expected

        out, err = capfd.readouterr()
        assert out == f"File already exists: {path}\nDo you want to overwrite? [y/N]: "
        assert err == ""
