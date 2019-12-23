from click.testing import CliRunner

from encore_api_cli.commands.analyze import cli


def test_analyze(mocker):
    client_mock = mocker.MagicMock()
    client_mock.return_value.analyze_keypoint.return_value = 'result'
    mocker.patch('encore_api_cli.commands.analyze.get_client', client_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', '--rule_id', '0', '1'])

    assert client_mock.call_count == 1

    assert result.exit_code == 0
    assert result.output == ''


def test_analyze_with_show(mocker):
    client_mock = mocker.MagicMock()
    client_mock.return_value.analyze_keypoint.return_value = 'result'
    mocker.patch('encore_api_cli.commands.analyze.get_client', client_mock)

    runner = CliRunner()
    result = runner.invoke(cli,
                           ['analyze', '--rule_id', '0', '--show_result', '1'])

    assert client_mock.call_count == 1

    assert result.exit_code == 0
    assert result.output == 'result\n'
