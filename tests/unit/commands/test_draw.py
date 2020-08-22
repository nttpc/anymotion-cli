import json
from textwrap import dedent

import pytest
from anymotion_sdk import RequestsError

from anymotion_cli.commands.draw import cli


class TestDraw(object):
    @pytest.mark.parametrize(
        "status, expected, exit_code",
        [
            ("SUCCESS", "Success: Drawing is complete.\n", 0),
            ("TIMEOUT", "Error: Drawing is timed out.", 1),
            ("FAILURE", "Error: Drawing failed.", 1),
        ],
    )
    @pytest.mark.parametrize(
        "id_option", [["--keypoint-id", "1"], ["--comparison-id", "1"]]
    )
    @pytest.mark.parametrize("rule_option", [[], ["--rule", "[]"]])
    @pytest.mark.parametrize("bg_rule_option", [[], ["--bg-rule", "[]"]])
    def test_valid(
        self,
        runner,
        make_client,
        status,
        expected,
        exit_code,
        id_option,
        rule_option,
        bg_rule_option,
    ):
        drawing_id = 111
        client_mock = make_client(status=status, drawing_id=drawing_id)

        args = ["draw", "--download"] + id_option + rule_option + bg_rule_option
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == exit_code
        assert result.output == dedent(
            f"Drawing started. (drawing id: {drawing_id})\n{expected}\n"
        )

    @pytest.mark.parametrize(
        "args",
        [
            ["draw", "--keypoint-id", "1", "--no-download"],
            ["draw", "--no-download", "--keypoint-id", "1"],
        ],
    )
    def test_valid_no_download(self, runner, make_client, args):
        client_mock = make_client()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            """\
            Drawing started. (drawing id: 111)
            Success: Drawing is complete.

            Skip download. To download it, run the following command.

            "amcli download 111"

            """
        )

    @pytest.mark.parametrize("rule", [[], {}, {"rule": []}])
    def test_valid_rule_file(self, tmp_path, runner, make_client, rule):
        client_mock = make_client()
        rule_file = tmp_path / "rule.json"
        rule_file.write_text(json.dumps(rule))

        result = runner.invoke(
            cli, ["draw", "--keypoint-id", "1", "--rule-file", rule_file, "--download"],
        )

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            """\
            Drawing started. (drawing id: 111)
            Success: Drawing is complete.

            """
        )

    def test_with_spinner(self, monkeypatch, runner, make_client):
        monkeypatch.setenv("ANYMOTION_USE_SPINNER", "true")
        client_mock = make_client()

        result = runner.invoke(cli, ["draw", "--keypoint-id", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert "Processing..." in result.output

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["draw", "--keypoint-id", "1", "--rule", "[1: 2]"],
                "Error: Rule format is invalid. Must be in JSON format.\n",
            ),
            (
                ["draw", "--keypoint-id", "1", "--rule", "1"],
                "Error: Rule format is invalid. Must be in list or object format.\n",
            ),
            (
                ["draw", "--keypoint-id", "1", "--bg-rule", "[1: 2]"],
                "Error: Rule format is invalid. Must be in JSON format.\n",
            ),
            (
                ["draw", "--keypoint-id", "1", "--bg-rule", "1"],
                "Error: Rule format is invalid. Must be in list or object format.\n",
            ),
        ],
    )
    def test_invalid_rule(self, runner, make_client, args, expected):
        client_mock = make_client()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 1
        assert result.output == expected

    def test_invalid_rule_file(self, tmp_path, runner, make_client):
        rule = {"rule": [], "invalid_key": True}

        client_mock = make_client()
        rule_file = tmp_path / "rule.json"
        rule_file.write_text(json.dumps(rule))

        result = runner.invoke(
            cli, ["draw", "--keypoint-id", "1", "--rule-file", rule_file]
        )

        assert client_mock.call_count == 0
        assert result.exit_code == 1
        assert result.output == "Error: Rule format is invalid.\n"

    def test_with_error(self, runner, make_client):
        client_mock = make_client(with_exception=True)
        result = runner.invoke(cli, ["draw", "--keypoint-id", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert "Error" in result.output

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["draw"],
                "Error: Either '--keypoint-id' or '--comparison-id' is required\n",
            ),
            (
                ["draw", "--keypoint-id", "1", "--comparison-id", "1"],
                "Error: Either '--keypoint-id' or '--comparison-id' is required\n",
            ),
            (
                ["draw", "--keypoint-id"],
                "Error: --keypoint-id option requires an argument\n",
            ),
            (
                ["draw", "--comparison-id"],
                "Error: --comparison-id option requires an argument\n",
            ),
            (
                ["draw", "--keypoint-id", "invalid_id"],
                (
                    "Error: Invalid value for '--keypoint-id': "
                    "invalid_id is not a valid integer\n"
                ),
            ),
            (
                ["draw", "--keypoint-id", "1", "--rule"],
                "Error: --rule option requires an argument\n",
            ),
            (
                ["draw", "--keypoint-id", "1", "--bg-rule"],
                "Error: --bg-rule option requires an argument\n",
            ),
            (
                ["draw", "--keypoint-id", "1", "--rule-file"],
                "Error: --rule-file option requires an argument\n",
            ),
        ],
    )
    def test_invalid_params(self, runner, make_client, args, expected):
        client_mock = make_client()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert result.output.endswith(expected)

    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                "--rule",
                '"--rule" and "--rule-file" options cannot be used at the same time.',
            ),
            (
                "--bg-rule",
                (
                    '"--bg-rule" and "--rule-file" options cannot be used '
                    "at the same time."
                ),
            ),
        ],
    )
    def test_invalid_params_both_rule(
        self, tmp_path, runner, make_client, option, expected
    ):
        client_mock = make_client()
        rule_file = tmp_path / "rule.json"
        rule_file.write_text("[]")

        result = runner.invoke(
            cli, ["draw", "--keypoint-id", "1", option, "[]", "--rule-file", rule_file]
        )

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert expected in result.output

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(status="SUCCESS", drawing_id=111, with_exception=False):
            client_mock = mocker.MagicMock()

            client_mock.return_value.draw_keypoint.return_value = drawing_id
            if status == "SUCCESS":
                url = "http://example.com/image.jpg"
            else:
                url = None

            wait_mock = client_mock.return_value.wait_for_drawing
            if with_exception:
                wait_mock.side_effect = RequestsError()
            else:
                wait_mock.return_value.status = status
                wait_mock.return_value.get.return_value = url

            mocker.patch("anymotion_cli.commands.draw.get_client", client_mock)
            mocker.patch("anymotion_cli.commands.draw.download", mocker.MagicMock())

            return client_mock

        return _make_client
