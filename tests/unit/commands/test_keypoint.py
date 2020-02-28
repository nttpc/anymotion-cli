from textwrap import dedent

import pytest
from encore_sdk import RequestsError

from encore_api_cli.commands.keypoint import cli


def test_keypoint(runner):
    result = runner.invoke(cli, ["keypoint"])
    assert result.exit_code == 0


class TestKeypointShow(object):
    def test_valid(self, mocker, runner):
        client_mock = self._get_client_mock(mocker)
        result = runner.invoke(cli, ["keypoint", "show", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
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
        )

    def test_valid_not_success(self, mocker, runner):
        client_mock = self._get_client_mock(mocker, status="FAILURE")
        result = runner.invoke(cli, ["keypoint", "show", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == "Error: Status is not SUCCESS.\n"

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["keypoint", "show"], 'Error: Missing argument "KEYPOINT_ID".\n',),
            (
                ["keypoint", "show", "invalid_id"],
                (
                    'Error: Invalid value for "KEYPOINT_ID": '
                    "invalid_id is not a valid integer\n"
                ),
            ),
        ],
    )
    def test_invalid_params(self, mocker, runner, args, expected):
        client_mock = self._get_client_mock(mocker)
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert result.output.endswith(expected)

    def test_with_pager(self, mocker, runner):
        client_mock = self._get_client_mock(mocker, num_data=10)

        result = runner.invoke(cli, ["keypoint", "show", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert '"1": [\n      10,\n      81\n    ]\n' in result.output

    def test_with_error(self, mocker, runner):
        client_mock = self._get_client_mock(mocker, with_exception=True)
        result = runner.invoke(cli, ["keypoint", "show", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert "Error" in result.output

    def _get_client_mock(
        self, mocker, status="SUCCESS", num_data=1, with_exception=False
    ):
        if status == "SUCCESS":
            data = [{"1": [i + 1, i * i]} for i in range(num_data)]
        else:
            data = None
        client_mock = mocker.MagicMock()
        if with_exception:
            client_mock.return_value.get_one_data.side_effect = RequestsError()
        else:
            client_mock.return_value.get_one_data.return_value = {
                "id": 111,
                "keypoint": data,
                "execStatus": status,
            }
        mocker.patch("encore_api_cli.commands.keypoint.get_client", client_mock)
        return client_mock


class TestKeypointList(object):
    @pytest.mark.parametrize(
        "args",
        [
            ["keypoint", "list"],
            ["keypoint", "list", "--status", "SUCCESS"],
            ["keypoint", "list", "--status", "success"],
        ],
    )
    def test_valid(self, mocker, runner, args):
        client_mock = self._get_client_mock(mocker)
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

    def test_with_spinner(self, mocker, monkeypatch, runner):
        monkeypatch.setenv("ANYMOTION_USE_SPINNER", "true")
        client_mock = self._get_client_mock(mocker)

        result = runner.invoke(cli, ["keypoint", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert "Retrieving..." in result.output

    def test_with_pager(self, mocker, runner):
        client_mock = self._get_client_mock(mocker, num_data=10)

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
                    'Error: Invalid value for "--status": invalid choice: '
                    "INVALID_STATUS. "
                    "(choose from SUCCESS, FAILURE, PROCESSING, UNPROCESSED)\n"
                ),
            ),
        ],
    )
    def test_invalid_params(self, mocker, runner, args, expected):
        client_mock = self._get_client_mock(mocker)
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert result.output.endswith(expected)

    def test_with_error(self, mocker, runner):
        client_mock = self._get_client_mock(mocker, with_exception=True)
        result = runner.invoke(cli, ["keypoint", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert "Error" in result.output

    def _get_client_mock(self, mocker, num_data=1, with_exception=False):
        client_mock = mocker.MagicMock()
        if with_exception:
            client_mock.return_value.get_list_data.side_effect = RequestsError()
        else:
            data = [
                {"id": i + 1, "image": 2, "movie": None, "execStatus": "SUCCESS"}
                for i in range(num_data)
            ]
            client_mock.return_value.get_list_data.return_value = data
        mocker.patch("encore_api_cli.commands.keypoint.get_client", client_mock)
        return client_mock
