from textwrap import dedent

import pytest
from click.testing import CliRunner

from encore_api_cli.commands.analysis import cli


def test_analysis():
    runner = CliRunner()
    result = runner.invoke(cli, ["analysis"])

    assert result.exit_code == 0


class TestAnalysisShow(object):
    @pytest.mark.parametrize(
        "response, expected",
        [
            ({"result": [], "execStatus": "SUCCESS"}, "\n[]\n\n"),
            ({"execStatus": "FAILURE"}, "Status is not SUCCESS.\n"),
        ],
    )
    def test_valid(self, mocker, response, expected):
        client_mock = mocker.MagicMock()
        client_mock.return_value.get_one_data.return_value = response
        mocker.patch("encore_api_cli.commands.analysis.get_client", client_mock)

        runner = CliRunner()
        result = runner.invoke(cli, ["analysis", "show", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    def test_missing_args(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["analysis", "show"])

        assert result.exit_code == 2

    def test_invalid_params(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["analysis", "show", "not_value"])

        assert result.exit_code == 2


class TestAnalysisList(object):
    def test_valid(self, mocker):
        expected = dedent(
            """\

                [
                  {
                    "id": 1
                  }
                ]

            """
        )

        client_mock = mocker.MagicMock()
        client_mock.return_value.get_list_data.return_value = [{"id": 1}]
        mocker.patch("encore_api_cli.commands.analysis.get_client", client_mock)

        runner = CliRunner()
        result = runner.invoke(cli, ["analysis", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected
