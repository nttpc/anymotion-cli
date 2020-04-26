from textwrap import dedent

import pytest
from encore_sdk import RequestsError

from anymotion_cli.commands.analysis import cli


def test_analysis(runner):
    result = runner.invoke(cli, ["analysis"])
    assert result.exit_code == 0


class TestAnalysisShow(object):
    @pytest.mark.parametrize(
        "args, status, expected",
        [
            (
                ["analysis", "show", "1"],
                "SUCCESS",
                dedent(
                    """\

                    {
                      "id": 111,
                      "result": [
                        {
                          "analysisType": "angle",
                          "values": [
                            180
                          ]
                        }
                      ],
                      "execStatus": "SUCCESS"
                    }

                    """
                ),
            ),
            (
                ["analysis", "show", "1"],
                "FAILURE",
                dedent(
                    """\

                    {
                      "id": 111,
                      "result": null,
                      "execStatus": "FAILURE"
                    }

                    """
                ),
            ),
            (
                ["analysis", "show", "1", "--no-result"],
                "SUCCESS",
                dedent(
                    """\

                    {
                      "id": 111,
                      "execStatus": "SUCCESS"
                    }

                    """
                ),
            ),
            (
                ["analysis", "show", "1", "--no-result"],
                "FAILURE",
                dedent(
                    """\

                    {
                      "id": 111,
                      "execStatus": "FAILURE"
                    }

                    """
                ),
            ),
        ],
    )
    def test_valid(self, runner, make_client, args, status, expected):
        client_mock = make_client(status)
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.parametrize(
        "args",
        [
            ["analysis", "show", "1", "--only"],
            ["analysis", "show", "1", "--only-result"],
            ["analysis", "show", "1", "--only", "--only-result"],
        ],
    )
    @pytest.mark.parametrize(
        "status, expected",
        [
            (
                "SUCCESS",
                dedent(
                    """\

                    [
                      {
                        "analysisType": "angle",
                        "values": [
                          180
                        ]
                      }
                    ]

                    """
                ),
            ),
        ],
    )
    def test_with_only(self, runner, make_client, args, status, expected):
        client_mock = make_client(status)
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.parametrize(
        "args",
        [
            ["analysis", "show", "1", "--only"],
            ["analysis", "show", "1", "--only-result"],
            ["analysis", "show", "1", "--only", "--only-result"],
        ],
    )
    @pytest.mark.parametrize(
        "status, expected", [("FAILURE", "Error: Status is not SUCCESS.\n")],
    )
    def test_with_only_with_error(self, runner, make_client, args, status, expected):
        client_mock = make_client(status)
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert result.output == expected

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["analysis", "show"], "Error: Missing argument 'ANALYSIS_ID'.\n"),
            (
                ["analysis", "show", "invalid_id"],
                (
                    "Error: Invalid value for 'ANALYSIS_ID': "
                    "invalid_id is not a valid integer\n",
                ),
            ),
            (
                ["analysis", "show", "1", "--only", "--no-result"],
                (
                    'Error: "--only, --only-result" and "--no-result" options '
                    "cannot be used at the same time.\n"
                ),
            ),
            (
                ["analysis", "show", "1", "--only-result", "--no-result"],
                (
                    'Error: "--only, --only-result" and "--no-result" options '
                    "cannot be used at the same time.\n"
                ),
            ),
        ],
    )
    def test_invalid_params(self, runner, make_client, args, expected):
        client_mock = make_client()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert result.output.endswith(expected)

    def test_with_error(self, runner, make_client):
        client_mock = make_client(with_exception=True)
        result = runner.invoke(cli, ["analysis", "show", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert result.output == "Error: \n"

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(status="SUCCESS", with_exception=False):
            client_mock = mocker.MagicMock()
            if status == "SUCCESS":
                data = [{"analysisType": "angle", "values": [180]}]
            else:
                data = None
            if with_exception:
                client_mock.return_value.get_analysis.side_effect = RequestsError()
            else:
                client_mock.return_value.get_analysis.return_value = {
                    "id": 111,
                    "result": data,
                    "execStatus": status,
                }
            mocker.patch("anymotion_cli.commands.analysis.get_client", client_mock)
            return client_mock

        return _make_client


class TestAnalysisList(object):
    @pytest.mark.parametrize(
        "args",
        [
            ["analysis", "list"],
            ["analysis", "list", "--status", "SUCCESS"],
            ["analysis", "list", "--status", "success"],
        ],
    )
    def test_valid(self, runner, make_client, args):
        client_mock = make_client()
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

        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    def test_with_spinner(self, monkeypatch, runner, make_client):
        monkeypatch.setenv("ANYMOTION_USE_SPINNER", "true")
        client_mock = make_client()

        result = runner.invoke(cli, ["analysis", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert "Retrieving..." in result.output

    def test_with_pager(self, runner, make_client):
        client_mock = make_client(num_data=10)

        result = runner.invoke(cli, ["analysis", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert '"id": 10' in result.output

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["analysis", "list", "--status"],
                "Error: --status option requires an argument\n",
            ),
            (
                ["analysis", "list", "--status", "INVALID_STATUS"],
                (
                    "Error: Invalid value for '--status': invalid choice: "
                    "INVALID_STATUS. "
                    "(choose from SUCCESS, FAILURE, PROCESSING, UNPROCESSED)\n"
                ),
            ),
        ],
    )
    def test_invalid_params(self, runner, make_client, args, expected):
        client_mock = make_client()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert result.output.endswith(expected)

    def test_with_error(self, runner, make_client):
        client_mock = make_client(with_exception=True)
        result = runner.invoke(cli, ["analysis", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert "Error" in result.output

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(num_data=1, with_exception=False):
            client_mock = mocker.MagicMock()
            if with_exception:
                client_mock.return_value.get_analyses.side_effect = RequestsError()
            else:
                data = [{"id": i + 1, "execStatus": "SUCCESS"} for i in range(num_data)]
                client_mock.return_value.get_analyses.return_value = data
            mocker.patch("anymotion_cli.commands.analysis.get_client", client_mock)
            return client_mock

        return _make_client
