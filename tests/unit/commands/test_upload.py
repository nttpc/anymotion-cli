from click.testing import CliRunner

from encore_api_cli.commands.upload import cli
from encore_api_cli.sdk.exceptions import FileTypeError, RequestsError


def test_upload(mocker, tmp_path):
    client_mock = mocker.MagicMock()
    client_mock.return_value.upload_to_s3.return_value = ("1", "image")
    mocker.patch("encore_api_cli.commands.upload.get_client", client_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ["upload", str(tmp_path)])

    assert client_mock.call_count == 1
    assert result.exit_code == 0


def test_upload_with_FileTypeError(mocker, tmp_path):
    message = (
        f"The extension of the file {tmp_path} must be .mp4, .mov, .jpg, .jpeg or .png."
    )
    client_mock = mocker.MagicMock()
    client_mock.return_value.upload_to_s3.side_effect = FileTypeError(message)
    mocker.patch("encore_api_cli.commands.upload.get_client", client_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ["upload", str(tmp_path)])

    assert client_mock.call_count == 1
    assert result.exit_code == 2
    assert message in result.output


def test_upload_with_RequestsError(mocker, tmp_path):
    message = "POST https://dev.example.jp/v1/oauth/accesstokens is failed."
    client_mock = mocker.MagicMock()
    client_mock.return_value.upload_to_s3.side_effect = RequestsError(message)
    mocker.patch("encore_api_cli.commands.upload.get_client", client_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ["upload", str(tmp_path)])

    assert client_mock.call_count == 1
    assert result.exit_code == 1
    assert message in result.output
