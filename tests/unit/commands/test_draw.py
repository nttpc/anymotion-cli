import pytest
from click.testing import CliRunner

from encore_api_cli.commands.draw import cli


@pytest.fixture
def client_mock(mocker):
    client_mock = mocker.MagicMock()
    client_mock.return_value.draw_keypoint.return_value = 2
    client_mock.return_value.wait_for_drawing.return_value = ("SUCCESS", "url")
    client_mock.return_value.download.return_value = None
    mocker.patch("encore_api_cli.commands.draw.get_client", client_mock)
    yield client_mock


@pytest.mark.parametrize(
    "params", [["draw", "1"], ["draw", "1", "--rule", "[]"]],
)
def test_draw(client_mock, params):
    runner = CliRunner()
    result = runner.invoke(cli, params)

    assert client_mock.call_count == 1
    assert result.exit_code == 0
    assert result.output == ""


@pytest.mark.parametrize(
    "rule, expected",
    [
        ("[1: 2]", "Error: Rule format is invalid. Must be in JSON format.\n"),
        ("{}", "Error: Rule format is invalid. Must be in list format.\n"),
    ],
)
def test_draw_with_invald_rule(client_mock, rule, expected):
    runner = CliRunner()
    result = runner.invoke(cli, ["draw", "1", "--rule", rule])

    assert client_mock.call_count == 1
    assert result.exit_code == 1
    assert result.output == expected
