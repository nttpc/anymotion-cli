from click.testing import CliRunner

from encore_api_cli.commands.draw import cli


def test_draw(mocker):
    client_mock = mocker.MagicMock()
    client_mock.return_value.draw_keypoint.return_value = 'url'
    client_mock.return_value.download.return_value = None
    mocker.patch('encore_api_cli.commands.draw.get_client', client_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ['draw', '1'])

    assert client_mock.call_count == 1
    assert result.exit_code == 0
    assert result.output == ''
