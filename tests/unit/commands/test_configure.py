from pathlib import Path
import textwrap

from click.testing import CliRunner

from encore_api_cli.commands.configure import cli

base_url = 'http://api.example.com'


def test_configure(mocker, tmpdir):
    default_url = 'https://api.customer.jp/'
    expected = textwrap.dedent(f"""\
        AnyMotion API URL [{default_url}]: {base_url}
        AnyMotion Client ID: client id
        AnyMotion Client Secret: client secret
    """)

    tmpdir = Path(tmpdir)
    mocker.patch('pathlib.Path.home', mocker.MagicMock(return_value=tmpdir))

    runner = CliRunner()
    result = runner.invoke(cli, ['configure'],
                           input=f'{base_url}\nclient id\nclient secret\n')

    assert not result.exception
    assert result.output == expected


def test_configure_list(mocker):
    expected = ''

    config_mock = mocker.MagicMock()
    config_mock.return_value.show.return_value = expected
    mocker.patch('encore_api_cli.commands.configure.Config', config_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ['configure', 'list'])

    assert result.exit_code == 0
    assert result.output == expected
