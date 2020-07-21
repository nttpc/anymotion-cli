from textwrap import dedent

import pytest
from anymotion_sdk import RequestsError

from anymotion_cli.commands.draw import cli


class TestDraw(object):
    @pytest.mark.parametrize(
        "args",
        [
            ["draw", "1", "--download"],
            ["draw", "1", "--rule", "[]", "--download"],
            ["draw", "--rule", "[]", "1", "--download"],
        ],
    )
    def test_valid(self, runner, make_client, args):
        client_mock = make_client()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            """\
            Drawing started. (drawing id: 111)
            Success: Drawing is complete.

            """
        )

    @pytest.mark.parametrize(
        "args", [["draw", "1", "--no-download"], ["draw", "--no-download", "1"]]
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

    @pytest.mark.parametrize(
        "status, expected",
        [
            ("TIMEOUT", "Error: Drawing is timed out."),
            ("FAILURE", "Error: Drawing failed."),
        ],
    )
    def test_valid_not_success(self, runner, make_client, status, expected):
        client_mock = make_client(status=status)
        result = runner.invoke(cli, ["draw", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert result.output == dedent(
            f"""\
            Drawing started. (drawing id: 111)
            {expected}
            """
        )

    def test_valid_rule_file(self, tmp_path, runner, make_client):
        client_mock = make_client()
        rule_file = tmp_path / "rule.json"
        rule_file.write_text("[]")

        result = runner.invoke(
            cli, ["draw", "1", "--rule-file", rule_file, "--download"]
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

        result = runner.invoke(cli, ["draw", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert "Processing..." in result.output

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["draw", "1", "--rule", "[1: 2]"],
                "Error: Rule format is invalid. Must be in JSON format.\n",
            ),
            (
                ["draw", "1", "--rule", "1"],
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

    def test_with_error(self, runner, make_client):
        client_mock = make_client(with_exception=True)
        result = runner.invoke(cli, ["draw", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert "Error" in result.output

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["draw", "invalid_id"], "Error: Invalid value for 'KEYPOINT_ID'"),
            (["draw"], "Error: Missing argument 'KEYPOINT_ID'"),
            (["draw", "--rule", "1"], "Error: Missing argument 'KEYPOINT_ID'"),
            (["draw", "--no-download"], "Error: Missing argument 'KEYPOINT_ID'"),
            (["draw", "--rule"], "Error: --rule option requires an argument"),
            (["draw", "1", "--rule"], "Error: --rule option requires an argument"),
        ],
    )
    def test_invalid_params(self, runner, make_client, args, expected):
        client_mock = make_client()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert expected in result.output

    def test_invalid_params_both_rule(self, tmp_path, runner, make_client):
        client_mock = make_client()
        rule_file = tmp_path / "rule.json"
        rule_file.write_text("[]")

        result = runner.invoke(
            cli, ["draw", "1", "--rule", "[]", "--rule-file", rule_file]
        )

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert (
            '"--rule" and "--rule-file" options cannot be used at the same time.'
            in result.output
        )

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(status="SUCCESS", with_exception=False):
            client_mock = mocker.MagicMock()
            client_mock.return_value.draw_keypoint.return_value = 111
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
