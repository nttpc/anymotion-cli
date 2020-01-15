import pytest
from click.testing import CliRunner
from textwrap import dedent

from encore_api_cli.commands.draw import cli


class TestDraw(object):
    @pytest.fixture
    def client_mock(self, mocker):
        client_mock = mocker.MagicMock()
        client_mock.return_value.draw_keypoint.return_value = 111
        client_mock.return_value.wait_for_drawing.return_value = (
            "SUCCESS",
            "http://example.com/image.jpg",
        )
        client_mock.return_value.download.return_value = None
        mocker.patch("encore_api_cli.commands.draw.get_client", client_mock)
        yield client_mock

    @pytest.mark.parametrize(
        "args",
        [["draw", "1"], ["draw", "1", "--rule", "[]"], ["draw", "--rule", "[]", "1"]],
    )
    def test_valid(self, client_mock, args):
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            """\
                Drawing started. (drawing_id: 111)
                Success: Drawing is complete.
                Downloaded the file to image.jpg.
            """
        )

    @pytest.mark.parametrize(
        "args", [["draw", "1", "--no-download"], ["draw", "--no-download", "1"]]
    )
    def test_valid_no_download(self, client_mock, args):
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            f"""\
                Drawing started. (drawing_id: 111)
                Success: Drawing is complete.
            """
        )

    def test_valid_skip_donwload(self, mocker, client_mock):
        message = dedent(
            """\
                Skip download. To download it, run the following command.

                "%(prog)s download %(drawing_id)s"
            """
        )
        check_download_mock = mocker.MagicMock(return_value=(False, message, None))
        mocker.patch("encore_api_cli.commands.draw.check_download", check_download_mock)

        runner = CliRunner()
        result = runner.invoke(cli, ["draw", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert (
            result.output
            == "Drawing started. (drawing_id: 111)\n"
            + "Success: Drawing is complete.\n"
            + message % {"prog": "cli", "drawing_id": "111"}
            + "\n"
        )

    @pytest.mark.parametrize(
        "status, message",
        [("TIMEOUT", "Drawing is timed out."), ("FAILURE", "Drawing failed.")],
    )
    def test_valid_not_success(self, mocker, status, message):
        client_mock = mocker.MagicMock()
        client_mock.return_value.draw_keypoint.return_value = 111
        client_mock.return_value.wait_for_drawing.return_value = (status, None)
        client_mock.return_value.download.return_value = None
        mocker.patch("encore_api_cli.commands.draw.get_client", client_mock)

        runner = CliRunner()
        result = runner.invoke(cli, ["draw", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            f"""\
                Drawing started. (drawing_id: 111)
                {message}
            """
        )

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["draw", "1", "--rule", "[1: 2]"],
                "Error: Rule format is invalid. Must be in JSON format.\n",
            ),
            (
                ["draw", "1", "--rule", "{}"],
                "Error: Rule format is invalid. Must be in list format.\n",
            ),
        ],
    )
    def test_invalid_rule(self, client_mock, args, expected):
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert result.output == expected

    @pytest.mark.parametrize("args", [["draw", "invalid_id"]])
    def test_invalid_params(self, client_mock, args):
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert 'Error: Invalid value for "KEYPOINT_ID"' in result.output

    @pytest.mark.parametrize(
        "args", [["draw"], ["draw", "--rule", "1"], ["draw", "--no-download"]]
    )
    def test_missing_args(self, client_mock, args):
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert 'Error: Missing argument "KEYPOINT_ID"' in result.output

    @pytest.mark.parametrize("args", [["draw", "--rule"], ["draw", "1", "--rule"]])
    def test_missing_params(self, client_mock, args):
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert "Error: --rule option requires an argument" in result.output
