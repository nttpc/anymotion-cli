from click.testing import CliRunner

from encore_api_cli.commands.upload import cli
from encore_api_cli.exceptions import InvalidFileType
from encore_api_cli.exceptions import RequestsError


def test_upload(mocker, tmp_path):
    client_mock = mocker.MagicMock()
    client_mock.return_value.upload_to_s3.return_value = ('1', 'image')
    mocker.patch('encore_api_cli.commands.upload.get_client', client_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ['upload', str(tmp_path)])

    assert client_mock.call_count == 1
    assert result.exit_code == 0
    assert result.output == f'Success: Uploaded {tmp_path} to ' \
        'the cloud storage. (image_id: 1)\n'


def test_upload_with_InvalidFileType(mocker, tmp_path):
    message = (f'File {tmp_path} must have '
               'a .mp4, .mov, .jpg, .jpeg or .png extension.')
    client_mock = mocker.MagicMock()
    client_mock.return_value.upload_to_s3.side_effect = InvalidFileType(
        message)
    mocker.patch('encore_api_cli.commands.upload.get_client', client_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ['upload', str(tmp_path)])

    assert client_mock.call_count == 1
    assert result.exit_code == 2
    assert message in result.output


def test_upload_with_RequestsError(mocker, tmp_path):
    message = 'POST https://dev.example.jp/v1/oauth/accesstokens is failed.'
    client_mock = mocker.MagicMock()
    client_mock.return_value.upload_to_s3.side_effect = RequestsError(message)
    mocker.patch('encore_api_cli.commands.upload.get_client', client_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ['upload', str(tmp_path)])

    assert client_mock.call_count == 1
    assert result.exit_code == 1
    assert message in result.output
