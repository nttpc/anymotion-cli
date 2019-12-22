from click.testing import CliRunner

from encore_api_cli.commands.upload import cli


def test_upload(mocker, tmp_path):
    client_mock = mocker.MagicMock()
    client_mock.return_value.upload_to_s3.return_value = ('1', 'image')
    mocker.patch('encore_api_cli.commands.upload.get_client', client_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ['upload', str(tmp_path)])

    assert client_mock.call_count == 1
    assert result.exit_code == 0
    assert result.output == 'Uploaded the image file to ' \
        'cloud storage (image_id: 1)\n'
