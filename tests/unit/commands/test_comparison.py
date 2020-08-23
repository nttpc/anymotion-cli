from textwrap import dedent

import pytest
from anymotion_sdk import RequestsError

from anymotion_cli.commands.comparison import cli


def test_comparison(runner):
    result = runner.invoke(cli, ["comparison"])
    assert result.exit_code == 0


class TestComparisonShow(object):
    @pytest.mark.parametrize(
        "args, status, expected",
        [
            (
                ["comparison", "show", "111"],
                "SUCCESS",
                dedent(
                    """\

                    {
                      "id": 111,
                      "target": 222,
                      "source": 333,
                      "difference": [
                        {
                          "nose": {
                            "distance": 0.0,
                            "direction": 0.0
                          }
                        }
                      ],
                      "execStatus": "SUCCESS"
                    }

                    """
                ),
            ),
            (
                ["comparison", "show", "111"],
                "FAILURE",
                dedent(
                    """\

                    {
                      "id": 111,
                      "target": 222,
                      "source": 333,
                      "difference": null,
                      "execStatus": "FAILURE"
                    }

                    """
                ),
            ),
            (
                ["comparison", "show", "111", "--no-difference"],
                "SUCCESS",
                dedent(
                    """\

                    {
                      "id": 111,
                      "target": 222,
                      "source": 333,
                      "execStatus": "SUCCESS"
                    }

                    """
                ),
            ),
            (
                ["comparison", "show", "111", "--no-difference"],
                "FAILURE",
                dedent(
                    """\

                    {
                      "id": 111,
                      "target": 222,
                      "source": 333,
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
            ["comparison", "show", "111", "--only"],
            ["comparison", "show", "111", "--only-difference"],
            ["comparison", "show", "111", "--only", "--only-difference"],
        ],
    )
    @pytest.mark.parametrize(
        "status, expected, exit_code",
        [
            (
                "SUCCESS",
                dedent(
                    """\

                    [
                      {
                        "nose": {
                          "distance": 0.0,
                          "direction": 0.0
                        }
                      }
                    ]

                    """
                ),
                0,
            ),
            ("FAILURE", "Error: Status is not SUCCESS.\n", 1),
        ],
    )
    def test_with_only(self, runner, make_client, args, status, expected, exit_code):
        client_mock = make_client(status)
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == exit_code
        assert result.output == expected

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["comparison", "show"], "Error: Missing argument 'COMPARISON_ID'.\n"),
            (
                ["comparison", "show", "invalid_id"],
                (
                    "Error: Invalid value for 'COMPARISON_ID': "
                    "invalid_id is not a valid integer\n",
                ),
            ),
            (
                ["comparison", "show", "111", "--only", "--no-difference"],
                (
                    'Error: "--only, --only-difference" and "--no-difference" options '
                    "cannot be used at the same time.\n"
                ),
            ),
            (
                ["comparison", "show", "111", "--only-difference", "--no-difference"],
                (
                    'Error: "--only, --only-difference" and "--no-difference" options '
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
        result = runner.invoke(cli, ["comparison", "show", "111"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert result.output == "Error: requests error\n"

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(status="SUCCESS", with_exception=False):
            client_mock = mocker.MagicMock()
            if status == "SUCCESS":
                data = [{"nose": {"distance": 0.0, "direction": 0.0}}]
            else:
                data = None

            comparison_mock = client_mock.return_value.get_comparison
            if with_exception:
                comparison_mock.side_effect = RequestsError("requests error")
            else:
                comparison_mock.return_value = {
                    "id": 111,
                    "target": 222,
                    "source": 333,
                    "difference": data,
                    "execStatus": status,
                }
            mocker.patch("anymotion_cli.commands.comparison.get_client", client_mock)
            return client_mock

        return _make_client


class TestComparisonList(object):
    @pytest.mark.parametrize(
        "args",
        [
            ["comparison", "list"],
            ["comparison", "list", "--status", "SUCCESS"],
            ["comparison", "list", "--status", "success"],
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

        result = runner.invoke(cli, args, catch_exceptions=False)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    def test_with_spinner(self, monkeypatch, runner, make_client):
        monkeypatch.setenv("ANYMOTION_USE_SPINNER", "true")
        client_mock = make_client()

        result = runner.invoke(cli, ["comparison", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert "Retrieving..." in result.output

    def test_with_pager(self, runner, make_client):
        client_mock = make_client(num_data=10)

        result = runner.invoke(cli, ["comparison", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert '"id": 10' in result.output

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["comparison", "list", "--status"],
                "Error: --status option requires an argument\n",
            ),
            (
                ["comparison", "list", "--status", "INVALID_STATUS"],
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
        result = runner.invoke(cli, ["comparison", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert result.output == "Error: requests error\n"

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(num_data=1, with_exception=False):
            client_mock = mocker.MagicMock()
            comparison_mock = client_mock.return_value.get_comparisons
            if with_exception:
                comparison_mock.side_effect = RequestsError("requests error")
            else:
                data = [{"id": i + 1, "execStatus": "SUCCESS"} for i in range(num_data)]
                comparison_mock.return_value = data
            mocker.patch("anymotion_cli.commands.comparison.get_client", client_mock)
            return client_mock

        return _make_client
