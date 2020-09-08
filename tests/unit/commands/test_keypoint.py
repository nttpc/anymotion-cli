from textwrap import dedent

import pytest
from anymotion_sdk import RequestsError

from anymotion_cli.commands.keypoint import cli


def test_keypoint(runner):
    result = runner.invoke(cli, ["keypoint"])
    assert result.exit_code == 0


class TestKeypointShow(object):
    @pytest.mark.parametrize(
        "args, status, expected",
        [
            (
                ["keypoint", "show", "111"],
                "SUCCESS",
                dedent(
                    """\

                    {
                      "id": 111,
                      "keypoint": [
                        {
                          "1": [
                            1,
                            0
                          ]
                        }
                      ],
                      "execStatus": "SUCCESS"
                    }

                    """
                ),
            ),
            (
                ["keypoint", "show", "111", "--join"],
                "SUCCESS",
                dedent(
                    """\

                    {
                      "id": 111,
                      "keypoint": [
                        {
                          "1": [
                            1,
                            0
                          ]
                        }
                      ],
                      "execStatus": "SUCCESS"
                    }

                    """
                ),
            ),
            (
                ["keypoint", "show", "111"],
                "FAILURE",
                dedent(
                    """\

                    {
                      "id": 111,
                      "keypoint": null,
                      "execStatus": "FAILURE"
                    }

                    """
                ),
            ),
            (
                ["keypoint", "show", "111", "--no-keypoint"],
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
                ["keypoint", "show", "111", "--no-keypoint"],
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
            ["keypoint", "show", "1", "--only"],
            ["keypoint", "show", "1", "--only-keypoint"],
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
                        "1": [
                          1,
                          0
                        ]
                      }
                    ]

                    """
                ),
            )
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
            ["keypoint", "show", "1", "--only"],
            ["keypoint", "show", "1", "--only-keypoint"],
        ],
    )
    @pytest.mark.parametrize(
        "status, expected",
        [("FAILURE", "Error: Status is not SUCCESS.\n")],
    )
    def test_with_only_not_success(self, runner, make_client, args, status, expected):
        client_mock = make_client(status)
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert result.output == expected

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["keypoint", "show"],
                "Error: Missing argument 'KEYPOINT_ID'.\n",
            ),
            (
                ["keypoint", "show", "invalid_id"],
                (
                    "Error: Invalid value for 'KEYPOINT_ID': "
                    "invalid_id is not a valid integer\n"
                ),
            ),
            (
                ["keypoint", "show", "1", "--only", "--no-keypoint"],
                (
                    'Error: "--only, --only-keypoint" and "--no-keypoint" options '
                    "cannot be used at the same time.\n"
                ),
            ),
            (
                ["keypoint", "show", "1", "--only-keypoint", "--no-keypoint"],
                (
                    'Error: "--only, --only-keypoint" and "--no-keypoint" options '
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

    @pytest.mark.parametrize(
        "args",
        [
            ["keypoint", "show", "1", "--only"],
            ["keypoint", "show", "1", "--only-keypoint"],
        ],
    )
    def test_with_pager(self, runner, make_client, args):
        client_mock = make_client(num_data=10)

        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert '"1": [\n      10,\n      81\n    ]\n' in result.output

    def test_with_error(self, runner, make_client):
        client_mock = make_client(with_exception=True)
        result = runner.invoke(cli, ["keypoint", "show", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert result.output == "Error: \n"

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(status="SUCCESS", num_data=1, with_exception=False):
            if status == "SUCCESS":
                data = [{"1": [i + 1, i * i]} for i in range(num_data)]
            else:
                data = None
            client_mock = mocker.MagicMock()
            if with_exception:
                client_mock.return_value.get_keypoint.side_effect = RequestsError()
            else:
                client_mock.return_value.get_keypoint.return_value = {
                    "id": 111,
                    "keypoint": data,
                    "execStatus": status,
                }
            mocker.patch("anymotion_cli.commands.keypoint.get_client", client_mock)
            return client_mock

        return _make_client


class TestKeypointList(object):
    @pytest.mark.parametrize(
        "args",
        [
            ["keypoint", "list"],
            ["keypoint", "list", "--status", "SUCCESS"],
            ["keypoint", "list", "--status", "success"],
        ],
    )
    def test_valid(self, runner, make_client, args):
        client_mock = make_client()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            """\

                [
                  {
                    "id": 1,
                    "image": 2,
                    "movie": null,
                    "execStatus": "SUCCESS"
                  }
                ]

            """
        )

    def test_with_spinner(self, monkeypatch, runner, make_client):
        monkeypatch.setenv("ANYMOTION_USE_SPINNER", "true")
        client_mock = make_client()

        result = runner.invoke(cli, ["keypoint", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert "Retrieving..." in result.output

    def test_with_pager(self, runner, make_client):
        client_mock = make_client(num_data=10)

        result = runner.invoke(cli, ["keypoint", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert '"id": 10' in result.output

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["keypoint", "list", "--status"],
                "Error: --status option requires an argument\n",
            ),
            (
                ["keypoint", "list", "--status", "INVALID_STATUS"],
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
        result = runner.invoke(cli, ["keypoint", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert "Error" in result.output

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(num_data=1, with_exception=False):
            client_mock = mocker.MagicMock()
            if with_exception:
                client_mock.return_value.get_keypoints.side_effect = RequestsError()
            else:
                data = [
                    {"id": i + 1, "image": 2, "movie": None, "execStatus": "SUCCESS"}
                    for i in range(num_data)
                ]
                client_mock.return_value.get_keypoints.return_value = data
            mocker.patch("anymotion_cli.commands.keypoint.get_client", client_mock)
            return client_mock

        return _make_client
