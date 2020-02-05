from textwrap import dedent

import pytest
from click.testing import CliRunner

from encore_api_cli.commands.analyze import cli


class TestAnalyze(object):
    @pytest.fixture
    def show_mock(self, mocker):
        show_mock = mocker.MagicMock()
        mocker.patch("encore_api_cli.commands.analyze.show", show_mock)
        yield show_mock

    @pytest.mark.parametrize(
        "args, show_mock_count",
        [
            (["analyze", "--rule", "[]", "1"], 0),
            (["analyze", "1", "--rule", "[]"], 0),
            (["analyze", "--rule", "[]", "--show-result", "1"], 1),
            (["analyze", "--rule", "[]", "1", "--show-result"], 1),
        ],
    )
    def test_valid(self, mocker, show_mock, args, show_mock_count):
        client_mock = self._client_mock(mocker)

        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert show_mock.call_count == show_mock_count
        assert result.exit_code == 0
        assert result.output == dedent(
            """\
                Analysis started. (analysis id: 111)
                Success: Analysis is complete.
            """
        )

    @pytest.mark.parametrize(
        "status, message",
        [
            ("TIMEOUT", "Analysis is timed out."),
            ("FAILURE", "Analysis failed: message"),
        ],
    )
    def test_valid_not_success(self, mocker, status, message):
        client_mock = self._client_mock(mocker, status)

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "1", "--rule", "[]"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            f"""\
                Analysis started. (analysis id: 111)
                {message}
            """
        )

    def test_valid_rule_file(self, mocker, tmp_path):
        client_mock = self._client_mock(mocker)
        rule_file = tmp_path / "rule.json"
        rule_file.write_text("[]")

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "1", "--rule-file", rule_file])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            """\
                Analysis started. (analysis id: 111)
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
    def test_invalid_rule(self, mocker, args, expected):
        client_mock = self._client_mock(mocker)

        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 1
        assert result.output == expected

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["analyze", "invalid_id"], 'Error: Invalid value for "KEYPOINT_ID"'),
            (["analyze"], 'Error: Missing argument "KEYPOINT_ID"'),
            (["analyze", "--rule", "1"], 'Error: Missing argument "KEYPOINT_ID"'),
            (["analyze", "--show-result"], 'Error: Missing argument "KEYPOINT_ID"'),
            (["analyze", "--rule"], "Error: --rule option requires an argument"),
            (["analyze", "1", "--rule"], "Error: --rule option requires an argument"),
            (["analyze", "1"], 'Either "rule" or "rule-file" options is required.'),
        ],
    )
    def test_invalid_params(self, mocker, args, expected):
        client_mock = self._client_mock(mocker)

        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert expected in result.output

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["analyze", "1", "--rule", "[]", "--rule-file", "<RULE_FILE>"],
                '"rule" and "rule-file" options cannot be used at the same time.',
            ),
        ],
    )
    def test_invalid_params_with_rule_file(self, mocker, tmp_path, args, expected):
        client_mock = self._client_mock(mocker)
        rule_file = tmp_path / "rule.json"
        rule_file.write_text("[]")
        args = map(lambda x: rule_file if x == "<RULE_FILE>" else x, args)

        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert expected in result.output

    def _client_mock(self, mocker, status="SUCCESS"):
        analysis_id = 111

        ResponseMock = mocker.MagicMock()
        ResponseMock.return_value.status = status
        if status == "FAILURE":
            ResponseMock.return_value.failure_detail = "message"

        client_mock = mocker.MagicMock()
        client_mock.return_value.analyze_keypoint.return_value = analysis_id
        client_mock.return_value.wait_for_analysis.return_value = ResponseMock()
        mocker.patch("encore_api_cli.commands.analyze.get_client", client_mock)

        return client_mock
