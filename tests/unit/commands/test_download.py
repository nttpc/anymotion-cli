import io
from pathlib import Path
from textwrap import dedent

import pytest
from encore_sdk import RequestsError

from encore_api_cli.commands.download import check_download, cli


class TestDownload(object):
    @pytest.mark.parametrize(
        "args, status, expected",
        [
            (["download", "111"], "SUCCESS", "Downloaded the file to {path}.\n",),
            (
                ["download", "111", "-o", "."],
                "SUCCESS",
                "Downloaded the file to {path}.\n",
            ),
            (
                ["download", "111", "--out-dir", "."],
                "SUCCESS",
                "Downloaded the file to {path}.\n",
            ),
            (
                ["download", "-o", ".", "111"],
                "SUCCESS",
                "Downloaded the file to {path}.\n",
            ),
        ],
    )
    def test_valid(self, runner, make_client_mock, args, status, expected):
        path = (Path(".") / "image.jpg").resolve()
        expected = expected.format(path=path)
        client_mock = make_client_mock(status)

        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    def test_valid_skip_download(self, mocker, runner, make_client_mock):
        client_mock = make_client_mock()
        message = dedent(
            """\
                Skip download. To download it, run the following command.

                "%(prog)s download %(drawing_id)s"
            """
        )
        check_download_mock = mocker.MagicMock(return_value=(False, message, None))
        mocker.patch(
            "encore_api_cli.commands.download.check_download", check_download_mock
        )

        result = runner.invoke(cli, ["download", "111"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == message % {"prog": "amcli", "drawing_id": "111"} + "\n"

    @pytest.mark.parametrize("status", ["FAILURE", "TIMEOUT"])
    def test_with_response_error(self, runner, make_client_mock, status):
        client_mock = make_client_mock(status)

        result = runner.invoke(cli, ["download", "111"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert result.output == "Error: Unable to download because drawing failed.\n"

    @pytest.mark.parametrize(
        "with_wait_exception, with_download_exception", [(True, True), (False, True)]
    )
    def test_with_requests_error(
        self, runner, make_client_mock, with_wait_exception, with_download_exception
    ):
        client_mock = make_client_mock(
            with_wait_exception=with_wait_exception,
            with_download_exception=with_download_exception,
        )
        result = runner.invoke(cli, ["download", "111"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert "Error" in result.output

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["download"], 'Error: Missing argument "DRAWING_ID".\n'),
            (
                ["download", "invalid_id"],
                (
                    'Error: Invalid value for "DRAWING_ID": '
                    "invalid_id is not a valid integer\n",
                ),
            ),
            (["download", "-o"], "Error: -o option requires an argument\n"),
            (
                ["download", "--out-dir"],
                "Error: --out-dir option requires an argument\n",
            ),
            (
                ["download", "-o", "not_exist"],
                (
                    'Error: Invalid value for "-o" / "--out-dir": '
                    'Directory "not_exist" does not exist.\n'
                ),
            ),
        ],
    )
    def test_invalid_params(self, runner, args, expected):
        result = runner.invoke(cli, args)
        assert result.exit_code == 2
        assert result.output.endswith(expected)

    def test_invalid_params_with_not_directory(self, runner, make_path):
        path = make_path("image.jpg", is_file=True)
        expected = (
            'Error: Invalid value for "-o" / "--out-dir": '
            f'Directory "{path}" is a file.\n'
        )
        result = runner.invoke(cli, ["download", "-o", str(path)])

        assert result.exit_code == 2
        assert result.output.endswith(expected)

    @pytest.fixture
    def make_client_mock(self, mocker):
        def _make_client_mock(
            status="SUCCESS", with_wait_exception=False, with_download_exception=False
        ):
            if status == "SUCCESS":
                url = "http://example.com/image.jpg"
            else:
                url = None

            client_mock = mocker.MagicMock()

            wait_mock = client_mock.return_value.wait_for_drawing
            if with_wait_exception:
                wait_mock.side_effect = RequestsError()
            else:
                wait_mock.return_value.status = status
                wait_mock.return_value.get.return_value = url

            if with_download_exception:
                client_mock.return_value.download.side_effect = RequestsError()
            else:
                client_mock.return_value.download.return_value = None

            mocker.patch("encore_api_cli.commands.download.get_client", client_mock)
            mocker.patch(
                "encore_api_cli.commands.download.get_name_from_drawing_id",
                mocker.MagicMock(return_value="image"),
            )

            return client_mock

        return _make_client_mock


class TestCheckDownload(object):
    def test_not_exists(self, make_path):
        out_dir = make_path("out", is_dir=True)
        url = "https://example.com/image.jpg"
        is_ok, message, path = check_download(out_dir, url)

        assert is_ok is True
        assert message == f"Downloaded the file to \x1b[34m{out_dir}/image.jpg\x1b[0m."
        assert path == Path(f"{out_dir}/image.jpg")

    def test_exists_yes(self, monkeypatch, tmp_path):
        monkeypatch.setattr("sys.stdin", io.StringIO("y"))
        (tmp_path / "image.jpg").touch()

        out_dir = str(tmp_path)
        url = "https://example.com/image.jpg"
        is_ok, message, path = check_download(out_dir, url)

        assert is_ok is True
        assert message == f"Downloaded the file to \x1b[34m{tmp_path}/image.jpg\x1b[0m."
        assert path == Path(f"{tmp_path}/image.jpg")

    def test_exists_no(self, monkeypatch, tmp_path):
        monkeypatch.setattr("sys.stdin", io.StringIO("N"))
        (tmp_path / "image.jpg").touch()

        out_dir = str(tmp_path)
        url = "https://example.com/image.jpg"
        is_ok, message, path = check_download(out_dir, url)

        assert is_ok is False
        assert message == dedent(
            """\
                Skip download. To download it, run the following command.

                "%(prog)s download %(drawing_id)s"
            """
        )
        assert path == Path(f"{tmp_path}/image.jpg")
