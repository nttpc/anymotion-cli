from textwrap import dedent

import pytest
from click.testing import CliRunner

from encore_api_cli.commands.keypoint import cli


def test_keypoint():
    runner = CliRunner()
    result = runner.invoke(cli, ["keypoint"])

    assert result.exit_code == 0


class TestKeypointShow(object):
    @pytest.fixture
    def client_mock(self, mocker):
        client_mock = mocker.MagicMock()
        client_mock.return_value.get_one_data.return_value = {
            "id": 111,
            "keypoint": [{"1": [143, 195]}],
            "execStatus": "SUCCESS",
        }
        mocker.patch("encore_api_cli.commands.keypoint.get_client", client_mock)
        yield client_mock

    @pytest.mark.parametrize("args", [["keypoint", "show", "1"]])
    def test_valid(self, client_mock, args):
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            """\

                [
                  {
                    "1": [
                      143,
                      195
                    ]
                  }
                ]

            """
        )

    def test_valid_not_success(self, mocker):
        client_mock = mocker.MagicMock()
        client_mock.return_value.get_one_data.return_value = {
            "id": 111,
            "keypoint": None,
            "execStatus": "FAILURE",
        }
        mocker.patch("encore_api_cli.commands.keypoint.get_client", client_mock)

        runner = CliRunner()
        result = runner.invoke(cli, ["keypoint", "show", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == "Status is not SUCCESS.\n"

    def test_invalid_params(self, client_mock):
        runner = CliRunner()
        result = runner.invoke(cli, ["keypoint", "show", "invalid_id"])

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert 'Error: Invalid value for "KEYPOINT_ID"' in result.output

    def test_missing_args(self, client_mock):
        runner = CliRunner()
        result = runner.invoke(cli, ["keypoint", "show"])

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert 'Error: Missing argument "KEYPOINT_ID"' in result.output


class TestKeypointList(object):
    @pytest.fixture
    def client_mock(self, mocker):
        client_mock = mocker.MagicMock()
        client_mock.return_value.get_list_data.return_value = [
            {"id": 111, "keypoint": '[{"1": [143, 195]}]', "execStatus": "SUCCESS"}
        ]
        mocker.patch("encore_api_cli.commands.keypoint.get_client", client_mock)
        yield client_mock

    @pytest.mark.parametrize(
        "args", [["keypoint", "list"], ["keypoint", "list", "--status", "SUCCESS"]]
    )
    def test_valid(self, client_mock, args):
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        # TODO: check output

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["keypoint", "list", "--status"],
                "Error: --status option requires an argument",
            ),
            (
                ["keypoint", "list", "--status", "INVALID_STATUS"],
                'Error: Invalid value for "--status": invalid choice',
            )
        ],
    )
    def test_invalid_params(self, client_mock, args, expected):
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert expected in result.output
