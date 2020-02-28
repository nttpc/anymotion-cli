from textwrap import dedent

import pytest
from encore_sdk import RequestsError

from encore_api_cli.commands.drawing import cli


def test_drawing(runner):
    result = runner.invoke(cli, ["drawing"])
    assert result.exit_code == 0


class TestDrawingShow(object):
    def test_valid(self, mocker, runner):
        expected = dedent(
            """\

                {
                  "id": 1,
                  "execStatus": "SUCCESS"
                }

            """
        )

        client_mock = self._get_client_mock(mocker)
        result = runner.invoke(cli, ["drawing", "show", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["drawing", "show"], 'Error: Missing argument "DRAWING_ID".\n'),
            (
                ["drawing", "show", "invalid_id"],
                (
                    'Error: Invalid value for "DRAWING_ID": '
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

    def test_with_error(self, mocker, runner):
        client_mock = self._get_client_mock(mocker, with_exception=True)
        result = runner.invoke(cli, ["drawing", "show", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert "Error" in result.output

    def _get_client_mock(self, mocker, with_exception=False):
        client_mock = mocker.MagicMock()
        if with_exception:
            client_mock.return_value.get_one_data.side_effect = RequestsError()
        else:
            client_mock.return_value.get_one_data.return_value = {
                "id": 1,
                "execStatus": "SUCCESS",
            }
        mocker.patch("encore_api_cli.commands.drawing.get_client", client_mock)
        return client_mock


class TestDrawingList(object):
    @pytest.mark.parametrize(
        "args",
        [
            ["drawing", "list"],
            ["drawing", "list", "--status", "SUCCESS"],
            ["drawing", "list", "--status", "success"],
        ],
    )
    def test_valid(self, mocker, runner, args):
        client_mock = self._get_client_mock(mocker)
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

    def test_with_spinner(self, mocker, monkeypatch, runner):
        monkeypatch.setenv("ANYMOTION_USE_SPINNER", "true")
        client_mock = self._get_client_mock(mocker)

        result = runner.invoke(cli, ["drawing", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert "Retrieving..." in result.output

    def test_with_pager(self, mocker, runner):
        client_mock = self._get_client_mock(mocker, num_data=10)

        result = runner.invoke(cli, ["drawing", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert '"id": 10' in result.output

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["drawing", "list", "--status"],
                "Error: --status option requires an argument\n",
            ),
            (
                ["drawing", "list", "--status", "INVALID_STATUS"],
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
        result = runner.invoke(cli, ["drawing", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert "Error" in result.output

    def _get_client_mock(self, mocker, num_data=1, with_exception=False):
        client_mock = mocker.MagicMock()
        if with_exception:
            client_mock.return_value.get_list_data.side_effect = RequestsError()
        else:
            data = [{"id": i + 1, "execStatus": "SUCCESS"} for i in range(num_data)]
            client_mock.return_value.get_list_data.return_value = data
        mocker.patch("encore_api_cli.commands.drawing.get_client", client_mock)
        return client_mock
