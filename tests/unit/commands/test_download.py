import io
from pathlib import Path
from textwrap import dedent

import pytest
from click.testing import CliRunner

from encore_api_cli.commands.download import check_download, cli


class TestDownload(object):
    # TODO: --out_dir option test

    @pytest.fixture
    def client_mock(self, mocker):
        client_mock = mocker.MagicMock()
        client_mock.return_value.wait_for_drawing.return_value = ("SUCCESS", "url")
        client_mock.return_value.download.return_value = None
        mocker.patch("encore_api_cli.commands.download.get_client", client_mock)
        yield client_mock

    @pytest.mark.parametrize(
        "wait_for_drawing_return, expected",
        [
            (
                ("SUCCESS", "http://example.com/image.jpg"),
                "Downloaded the file to image.jpg.\n",
            ),
            (("SUCCESS", None), "Error: Unable to download because drawing failed.\n"),
            (("FAILURE", None), "Error: Unable to download because drawing failed.\n"),
            (("TIMEOUT", None), "Error: Unable to download because drawing failed.\n"),
        ],
    )
    def test_valid(self, mocker, wait_for_drawing_return, expected):
        client_mock = mocker.MagicMock()
        client_mock.return_value.wait_for_drawing.return_value = wait_for_drawing_return
        client_mock.return_value.download.return_value = None
        client_mock.return_value.get_name_from_drawing_id.return_value = "image"
        mocker.patch("encore_api_cli.commands.download.get_client", client_mock)

        runner = CliRunner()
        result = runner.invoke(cli, ["download", "111"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    def test_valid_skip_donwload(self, mocker, client_mock):
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

        runner = CliRunner()
        result = runner.invoke(cli, ["download", "111"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == message % {"prog": "amcli", "drawing_id": "111"} + "\n"

    def test_missing_args(self, client_mock):
        runner = CliRunner()
        result = runner.invoke(cli, ["download"])

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert 'Error: Missing argument "DRAWING_ID".' in result.output

    def test_invalid_params(self, client_mock):
        runner = CliRunner()
        result = runner.invoke(cli, ["download", "invalid_id"])

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert 'Error: Invalid value for "DRAWING_ID"' in result.output


class TestCheckDownload(object):
    def test_not_exists(self, tmp_path):
        out_dir = str(tmp_path)
        url = "https://example.com/image.jpg"
        is_ok, message, path = check_download(out_dir, url)

        assert is_ok is True
        assert message == f"Downloaded the file to \x1b[34m{tmp_path}/image.jpg\x1b[0m."
        assert path == Path(f"{tmp_path}/image.jpg")

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
