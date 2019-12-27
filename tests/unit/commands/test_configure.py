from pathlib import Path
import textwrap

from click.testing import CliRunner

from encore_api_cli.commands.configure import cli


def test_configure(mocker, tmpdir):
    default_url = 'https://api.customer.jp/'
    base_url = 'http://api.example.com'
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
    expected = textwrap.dedent("""\
        Name              Value
        ----------------  -----------------------
        profile           default
        api_url           https://api.example.jp/
        client_id         ****************t_id
        client_secret     ****************cret
        polling_interval  10
        timeout           600
    """)

    class SettingsMock(object):
        url = 'https://api.example.jp/'
        client_id = 'client_id'
        client_secret = 'client_secret'
        interval = 10
        timeout = 600

    settings_mock = mocker.MagicMock(return_value=SettingsMock())
    mocker.patch('encore_api_cli.commands.configure.Settings', settings_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ['configure', 'list'])

    assert result.exit_code == 0
    assert result.output == expected
