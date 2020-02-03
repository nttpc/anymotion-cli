from textwrap import dedent

import pytest
from click.testing import CliRunner

from encore_api_cli.commands.drawing import cli


def test_drawing():
    runner = CliRunner()
    result = runner.invoke(cli, ["drawing"])

    assert result.exit_code == 0


class TestDrawingShow(object):
    def test_valid(self, mocker):
        expected = dedent(
            """\

                {
                  "id": 1,
                  "execStatus": "SUCCESS"
                }

            """
        )

        client_mock = self._get_client_mock(mocker)
        runner = CliRunner()
        result = runner.invoke(cli, ["drawing", "show", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["drawing", "show"], 'Error: Missing argument "DRAWING_ID"'),
            (["drawing", "show", "not_value"], 'Error: Invalid value for "DRAWING_ID"'),
        ],
    )
    def test_invalid_params(self, mocker, args, expected):
        client_mock = self._get_client_mock(mocker)
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert expected in result.output

    def _get_client_mock(self, mocker):
        client_mock = mocker.MagicMock()
        client_mock.return_value.get_one_data.return_value = {
            "id": 1,
            "execStatus": "SUCCESS",
        }
        mocker.patch("encore_api_cli.commands.drawing.get_client", client_mock)
        return client_mock


class TestDrawingList(object):
    @pytest.mark.parametrize(
        "args", [["drawing", "list"], ["drawing", "list", "--status", "SUCCESS"]]
    )
    def test_valid(self, mocker, args):
        client_mock = self._client_mock(mocker)
        expected = dedent(
            """\

                [
                  {
                    "id": 1,
                    "execStatus": "SUCCESS"
                  }
                ]

            """
        )

        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["drawing", "list", "--status"],
                "Error: --status option requires an argument",
            ),
            (
                ["drawing", "list", "--status", "INVALID_STATUS"],
                'Error: Invalid value for "--status": invalid choice',
            )
        ],
    )
    def test_invalid_params(self, mocker, args, expected):
        client_mock = self._client_mock(mocker)

        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert expected in result.output

    def _client_mock(self, mocker):
        client_mock = mocker.MagicMock()
        client_mock.return_value.get_list_data.return_value = [
            {"id": 1, "execStatus": "SUCCESS"}
        ]
        mocker.patch("encore_api_cli.commands.drawing.get_client", client_mock)
        return client_mock
