from click.testing import CliRunner

from encore_api_cli.commands.download import cli


def test_download(mocker):
    client_mock = mocker.MagicMock()
    client_mock.return_value.wait_for_drawing.return_value = ("SUCCESS", "url")
    client_mock.return_value.download.return_value = None
    mocker.patch("encore_api_cli.commands.download.get_client", client_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ["download", "222"])

    assert client_mock.call_count == 1
    assert result.exit_code == 0
