from textwrap import dedent

import pytest
from anymotion_sdk import RequestsError

from anymotion_cli.commands.drawing import cli


def test_drawing(runner):
    result = runner.invoke(cli, ["drawing"])
    assert result.exit_code == 0


class TestDrawingShow(object):
    def test_valid(self, runner, make_client):
        expected = dedent(
            """\

                {
                  "id": 1,
                  "execStatus": "SUCCESS"
                }

            """
        )

        client_mock = make_client()
        result = runner.invoke(cli, ["drawing", "show", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["drawing", "show"], "Error: Missing argument 'DRAWING_ID'.\n"),
            (
                ["drawing", "show", "invalid_id"],
                (
                    "Error: Invalid value for 'DRAWING_ID': "
                    "invalid_id is not a valid integer\n"
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
        result = runner.invoke(cli, ["drawing", "show", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert result.output == "Error: \n"

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(status="SUCCESS", with_exception=False):
            client_mock = mocker.MagicMock()
            if with_exception:
                client_mock.return_value.get_drawing.side_effect = RequestsError()
            else:
                client_mock.return_value.get_drawing.return_value = {
                    "id": 1,
                    "execStatus": status,
                }
            mocker.patch("anymotion_cli.commands.drawing.get_client", client_mock)
            return client_mock

        return _make_client


class TestDrawingList(object):
    @pytest.mark.parametrize(
        "args",
        [
            ["drawing", "list"],
            ["drawing", "list", "--status", "SUCCESS"],
            ["drawing", "list", "--status", "success"],
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

        result = runner.invoke(cli, ["drawing", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert "Retrieving..." in result.output

    def test_with_pager(self, runner, make_client):
        client_mock = make_client(num_data=10)

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
        result = runner.invoke(cli, ["drawing", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert "Error" in result.output

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(num_data=1, with_exception=False):
            client_mock = mocker.MagicMock()
            if with_exception:
                client_mock.return_value.get_drawings.side_effect = RequestsError()
            else:
                data = [{"id": i + 1, "execStatus": "SUCCESS"} for i in range(num_data)]
                client_mock.return_value.get_drawings.return_value = data
            mocker.patch("anymotion_cli.commands.drawing.get_client", client_mock)
            return client_mock

        return _make_client
