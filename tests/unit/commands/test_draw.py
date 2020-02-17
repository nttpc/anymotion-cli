from pathlib import Path
from textwrap import dedent

import pytest

from encore_api_cli.commands.draw import cli
from encore_sdk import RequestsError


class TestDraw(object):
    @pytest.mark.parametrize(
        "args",
        [["draw", "1"], ["draw", "1", "--rule", "[]"], ["draw", "--rule", "[]", "1"]],
    )
    def test_valid(self, mocker, runner, args):
        path = (Path(".") / "image.jpg").resolve()
        client_mock = self._get_client_mock(mocker)
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            f"""\
                Drawing started. (drawing id: 111)
                Success: Drawing is complete.
                Downloaded the file to {path}.
            """
        )

    @pytest.mark.parametrize(
        "args", [["draw", "1", "--no-download"], ["draw", "--no-download", "1"]]
    )
    def test_valid_no_download(self, mocker, runner, args):
        client_mock = self._get_client_mock(mocker)
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            f"""\
                Drawing started. (drawing id: 111)
                Success: Drawing is complete.
            """
        )

    def test_valid_skip_donwload(self, mocker, runner):
        message = dedent(
            """\
                Skip download. To download it, run the following command.

                "%(prog)s download %(drawing_id)s"
            """
        )
        client_mock = self._get_client_mock(mocker)
        check_download_mock = mocker.MagicMock(return_value=(False, message, None))
        mocker.patch("encore_api_cli.commands.draw.check_download", check_download_mock)

        result = runner.invoke(cli, ["draw", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        message = message % {"prog": "amcli", "drawing_id": "111"}
        assert result.output == (
            "Drawing started. (drawing id: 111)\n"
            "Success: Drawing is complete.\n"
            f"{message}\n"
        )

    @pytest.mark.parametrize(
        "status, expected",
        [
            ("TIMEOUT", "Error: Drawing is timed out."),
            ("FAILURE", "Error: Drawing failed."),
        ],
    )
    def test_valid_not_success(self, mocker, runner, status, expected):
        client_mock = self._get_client_mock(mocker, status)
        result = runner.invoke(cli, ["draw", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            f"""\
                Drawing started. (drawing id: 111)
                {expected}
            """
        )

    def test_valid_rule_file(self, mocker, tmp_path, runner):
        path = (Path(".") / "image.jpg").resolve()
        client_mock = self._get_client_mock(mocker)
        rule_file = tmp_path / "rule.json"
        rule_file.write_text("[]")

        result = runner.invoke(cli, ["draw", "1", "--rule-file", rule_file])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            f"""\
                Drawing started. (drawing id: 111)
                Success: Drawing is complete.
                Downloaded the file to {path}.
            """
        )

    def test_with_spinner(self, mocker, monkeypatch, runner):
        monkeypatch.setenv("ANYMOTION_USE_SPINNER", "true")
        client_mock = self._get_client_mock(mocker)

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
    def test_invalid_rule(self, mocker, runner, args, expected):
        client_mock = self._get_client_mock(mocker)
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 1
        assert result.output == expected

    @pytest.mark.parametrize(
        "with_drawing_exception, with_download_exception", [(True, True), (False, True)]
    )
    def test_with_error(
        self, mocker, runner, with_drawing_exception, with_download_exception
    ):
        client_mock = self._get_client_mock(
            mocker,
            with_drawing_exception=with_drawing_exception,
            with_download_exception=with_download_exception,
        )
        result = runner.invoke(cli, ["draw", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert "Error" in result.output

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["draw", "invalid_id"], 'Error: Invalid value for "KEYPOINT_ID"'),
            (["draw"], 'Error: Missing argument "KEYPOINT_ID"'),
            (["draw", "--rule", "1"], 'Error: Missing argument "KEYPOINT_ID"'),
            (["draw", "--no-download"], 'Error: Missing argument "KEYPOINT_ID"'),
            (["draw", "--rule"], "Error: --rule option requires an argument"),
            (["draw", "1", "--rule"], "Error: --rule option requires an argument"),
        ],
    )
    def test_invalid_params(self, mocker, runner, args, expected):
        client_mock = self._get_client_mock(mocker)
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert expected in result.output

    def test_invalid_params_both_rule(self, mocker, tmp_path, runner):
        client_mock = self._get_client_mock(mocker)
        rule_file = tmp_path / "rule.json"
        rule_file.write_text("[]")

        result = runner.invoke(
            cli, ["draw", "1", "--rule", "[]", "--rule-file", rule_file]
        )

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert (
            '"rule" and "rule-file" options cannot be used at the same time.'
            in result.output
        )

    def _get_client_mock(
        self,
        mocker,
        status="SUCCESS",
        with_drawing_exception=False,
        with_download_exception=False,
    ):
        client_mock = mocker.MagicMock()
        client_mock.return_value.draw_keypoint.return_value = 111
        if status == "SUCCESS":
            url = "http://example.com/image.jpg"
            client_mock.return_value.get_name_from_drawing_id.return_value = "image"
        else:
            url = None

        if with_drawing_exception:
            client_mock.return_value.wait_for_drawing.side_effect = RequestsError()
        else:
            client_mock.return_value.wait_for_drawing.return_value = (
                status,
                url,
            )

        if with_download_exception:
            client_mock.return_value.download.side_effect = RequestsError()
        else:
            client_mock.return_value.download.return_value = None

        mocker.patch("encore_api_cli.commands.draw.get_client", client_mock)
        return client_mock
