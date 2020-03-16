from textwrap import dedent

import pytest
from encore_sdk import RequestsError

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
    def test_valid(self, mocker, runner, show_mock, args, show_mock_count):
        client_mock = self._get_client_mock(mocker)
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
            (
                "TIMEOUT",
                dedent(
                    """\
                    Analysis started. (analysis id: 111)
                    Error: Analysis is timed out.
                    """
                ),
            ),
            (
                "FAILURE",
                dedent(
                    """\
                    Analysis started. (analysis id: 111)
                    Error: Analysis failed.
                    message
                    """
                ),
            ),
        ],
    )
    def test_valid_not_success(self, mocker, runner, status, message):
        client_mock = self._get_client_mock(mocker, status)
        result = runner.invoke(cli, ["analyze", "1", "--rule", "[]"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert result.output == message

    def test_valid_rule_file(self, mocker, runner, tmp_path):
        client_mock = self._get_client_mock(mocker)
        rule_file = tmp_path / "rule.json"
        rule_file.write_text("[]")

        result = runner.invoke(cli, ["analyze", "1", "--rule-file", rule_file])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            """\
            Analysis started. (analysis id: 111)
            Success: Analysis is complete.
            """
        )

    def test_with_spinner(self, mocker, monkeypatch, runner):
        monkeypatch.setenv("ANYMOTION_USE_SPINNER", "true")
        client_mock = self._get_client_mock(mocker)

        result = runner.invoke(cli, ["analyze", "1", "--rule", "[]"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert "Processing..." in result.output

    @pytest.mark.parametrize(
        "with_analyze_exception, with_wait_exception", [(True, True), (False, True)]
    )
    def test_with_error(
        self, mocker, runner, with_analyze_exception, with_wait_exception
    ):
        client_mock = self._get_client_mock(
            mocker,
            with_analyze_exception=with_analyze_exception,
            with_wait_exception=with_wait_exception,
        )
        result = runner.invoke(cli, ["analyze", "1", "--rule", "[]"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert "Error" in result.output

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
    def test_invalid_rule(self, mocker, runner, args, expected):
        client_mock = self._get_client_mock(mocker)
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 1
        assert result.output == expected

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["analyze", "invalid_id"], "Error: Invalid value for 'KEYPOINT_ID'"),
            (["analyze"], "Error: Missing argument 'KEYPOINT_ID'"),
            (["analyze", "--rule", "1"], "Error: Missing argument 'KEYPOINT_ID'"),
            (["analyze", "--show-result"], "Error: Missing argument 'KEYPOINT_ID'"),
            (["analyze", "--rule"], "Error: --rule option requires an argument"),
            (["analyze", "1", "--rule"], "Error: --rule option requires an argument"),
            (["analyze", "1"], 'Either "rule" or "rule-file" options is required.'),
        ],
    )
    def test_invalid_params(self, mocker, runner, args, expected):
        client_mock = self._get_client_mock(mocker)
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
    def test_invalid_params_with_rule_file(
        self, mocker, runner, tmp_path, args, expected
    ):
        client_mock = self._get_client_mock(mocker)
        rule_file = tmp_path / "rule.json"
        rule_file.write_text("[]")
        args = map(lambda x: rule_file if x == "<RULE_FILE>" else x, args)

        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert expected in result.output

    def _get_client_mock(
        self,
        mocker,
        status="SUCCESS",
        with_analyze_exception=False,
        with_wait_exception=False,
    ):
        analysis_id = 111
        client_mock = mocker.MagicMock()

        if with_analyze_exception:
            client_mock.return_value.analyze_keypoint.side_effect = RequestsError()
        else:
            client_mock.return_value.analyze_keypoint.return_value = analysis_id

        wait_mock = client_mock.return_value.wait_for_analysis
        if with_wait_exception:
            wait_mock.side_effect = RequestsError()
        else:
            wait_mock.return_value.status = status
            if status == "FAILURE":
                wait_mock.return_value.failure_detail = "message"

        mocker.patch("encore_api_cli.commands.analyze.get_client", client_mock)
        return client_mock
