import pytest
from click.testing import CliRunner

from encore_api_cli.commands.analyze import cli


class TestAnalyze(object):
    @pytest.fixture
    def client_mock(self, mocker):
        analysis_id = 111
        client_mock = mocker.MagicMock()
        client_mock.return_value.analyze_keypoint.return_value = analysis_id
        client_mock.return_value.wait_for_analysis.return_value = "SUCCESS"
        mocker.patch("encore_api_cli.commands.analyze.get_client", client_mock)
        yield client_mock

    @pytest.mark.parametrize(
        "params", [["analyze", "1"], ["analyze", "1", "--rule", "[]"]],
    )
    def test_valid(self, client_mock, params):
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
    def test_invalid(self, client_mock, rule, expected):
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "1", "--rule", rule])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert result.output == expected


# TODO: add test
# def test_analyze_with_show(mocker):
#     analysis_id = 111

#     client_mock = mocker.MagicMock()
#     client_mock.return_value.analyze_keypoint.return_value = analysis_id
#     client_mock.return_value.wait_for_analysis.return_value = "SUCCESS"
#     mocker.patch("encore_api_cli.commands.analyze.get_client", client_mock)

#     runner = CliRunner()
#     result = runner.invoke(
#         cli, ["analyze", "--show_result", "1"], catch_exceptions=True
#     )

#     assert client_mock.call_count == 1

#     assert result.exit_code == 0
#     assert result.output == ""
