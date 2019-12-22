from tempfile import TemporaryDirectory
from pathlib import Path
from click.testing import CliRunner

from encore_api_cli.commands.configure import cli

base_url = 'http://api.example.com'


def test_configure(mocker):
    with TemporaryDirectory(prefix='pytest_') as tmp_dir:
        home_mock = mocker.MagicMock(return_value=Path(tmp_dir))
        mocker.patch('pathlib.Path.home', home_mock)

        runner = CliRunner()
        result = runner.invoke(cli, ['configure'],
                               input=f'{base_url}\ntoken\n')

        default_url = 'https://api.anymotion.jp/api/v1/'

        assert not result.exception
        assert result.output == \
            f'AnyMotion API URL [{default_url}]: {base_url}\n' \
            'AnyMotion Access Token: token\n'


def test_configure_list(mocker):
    expected = ''

    config_mock = mocker.MagicMock()
    config_mock.return_value.show.return_value = expected
    mocker.patch('encore_api_cli.commands.configure.Config', config_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ['configure', 'list'])

    assert result.exit_code == 0
    assert result.output == expected
