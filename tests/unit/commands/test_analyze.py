from textwrap import dedent

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

    @pytest.fixture
    def show_mock(self, mocker):
        show_mock = mocker.MagicMock()
        mocker.patch("encore_api_cli.commands.analyze.show", show_mock)
        yield show_mock

    @pytest.mark.parametrize(
        "args, show_mock_count",
        [
            (["analyze", "1"], 0),
            (["analyze", "--rule", "[]", "1"], 0),
            (["analyze", "1", "--rule", "[]"], 0),
            (["analyze", "--show_result", "1"], 1),
            (["analyze", "1", "--show_result"], 1),
        ],
    )
    def test_valid(self, client_mock, show_mock, args, show_mock_count):
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert show_mock.call_count == show_mock_count
        assert result.exit_code == 0
        assert result.output == dedent(
            """\
                Analysis started. (analysis_id: 111)
                Success: Analysis is complete.
            """
        )

    @pytest.mark.parametrize(
        "status, message",
        [("TIMEOUT", "Analysis is timed out."), ("FAILURE", "Analysis failed.")],
    )
    def test_valid_not_success(self, mocker, status, message):
        analysis_id = 111
        client_mock = mocker.MagicMock()
        client_mock.return_value.analyze_keypoint.return_value = analysis_id
        client_mock.return_value.wait_for_analysis.return_value = status
        mocker.patch("encore_api_cli.commands.analyze.get_client", client_mock)

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            f"""\
                Analysis started. (analysis_id: 111)
                {message}
            """
        )

    def test_valid_rule_file(self, tmp_path, client_mock):
        rule_file = tmp_path / "rule.json"
        rule_file.write_text("[]")

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "1", "--rule-file", rule_file])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            """\
                Analysis started. (analysis_id: 111)
                Success: Analysis is complete.
            """
        )

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["analyze", "--rule", "[1: 2]", "1"],
                "Error: Rule format is invalid. Must be in JSON format.\n",
            ),
            (
                ["analyze", "1", "--rule", "[1: 2]"],
                "Error: Rule format is invalid. Must be in JSON format.\n",
            ),
            (
                ["analyze", "--rule", '"1"', "1"],
                "Error: Rule format is invalid. Must be in list or object format.\n",
            ),
            (
                ["analyze", "1", "--rule", '"1"'],
                "Error: Rule format is invalid. Must be in list or object format.\n",
            ),
        ],
    )
    def test_invalid_rule(self, client_mock, args, expected):
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 1
        assert result.output == expected

    @pytest.mark.parametrize("args", [["analyze", "invalid_id"]])
    def test_invalid_params(self, client_mock, args):
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert 'Error: Invalid value for "KEYPOINT_ID"' in result.output

    @pytest.mark.parametrize(
        "args", [["analyze"], ["analyze", "--rule", "1"], ["analyze", "--show_result"]]
    )
    def test_missing_args(self, client_mock, args):
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert 'Error: Missing argument "KEYPOINT_ID"' in result.output

    @pytest.mark.parametrize(
        "args", [["analyze", "--rule"], ["analyze", "1", "--rule"]]
    )
    def test_missing_params(self, client_mock, args):
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert "Error: --rule option requires an argument" in result.output

    def test_invalid_params_both_rule(self, tmp_path, client_mock):
        rule_file = tmp_path / "rule.json"
        rule_file.write_text("[]")

        runner = CliRunner()
        result = runner.invoke(
            cli, ["analyze", "1", "--rule", "[]", "--rule-file", rule_file]
        )

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert (
            '"rule" and "rule_file" options cannot be used at the same time.'
            in result.output
        )
