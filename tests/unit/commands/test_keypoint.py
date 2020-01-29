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

    def test_valid(self, client_mock):
        runner = CliRunner()
        result = runner.invoke(cli, ["keypoint", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        # TODO: check output


class TestKeypointExtract(object):
    @pytest.mark.parametrize(
        "args, status, expected",
        [
            (
                ["keypoint", "extract", "--movie_id", "111"],
                "SUCCESS",
                "Success: Keypoint extraction is complete.",
            ),
            (
                ["keypoint", "extract", "--image_id", "111"],
                "SUCCESS",
                "Success: Keypoint extraction is complete.",
            ),
            (
                ["keypoint", "extract", "--movie_id", "111"],
                "TIMEOUT",
                "Keypoint extraction is timed out.",
            ),
            (
                ["keypoint", "extract", "--image_id", "111"],
                "TIMEOUT",
                "Keypoint extraction is timed out.",
            ),
            (
                ["keypoint", "extract", "--movie_id", "111"],
                "FAILURE",
                "Keypoint extraction failed.",
            ),
            (
                ["keypoint", "extract", "--image_id", "111"],
                "FAILURE",
                "Keypoint extraction failed.",
            ),
        ],
    )
    def test_valid(self, mocker, args, status, expected):
        keypoint_id = 111
        client_mock = self._get_client_mock(
            mocker, status=status, keypoint_id=keypoint_id
        )

        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == dedent(
            f"""\
                Keypoint extraction started. (keypoint_id: {keypoint_id})
                {expected}
            """
        )

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["keypoint", "extract"],
                'Error: Either "movie_id" or "image_id" is required',
            ),
            (
                ["keypoint", "extract", "--image_id", "1", "--movie_id", "1"],
                'Error: Either "movie_id" or "image_id" is required',
            ),
            (
                ["keypoint", "extract", "--image_id"],
                "Error: --image_id option requires an argument",
            ),
            (
                ["keypoint", "extract", "--movie_id"],
                "Error: --movie_id option requires an argument",
            ),
            (
                ["keypoint", "extract", "--movie_id", "invalid_id"],
                'Error: Invalid value for "--movie_id"',
            ),
            (
                ["keypoint", "extract", "--image_id", "invalid_id"],
                'Error: Invalid value for "--image_id"',
            ),
        ],
    )
    def test_invalid_params(self, mocker, args, expected):
        client_mock = self._get_client_mock(mocker)
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert expected in result.output

    def _get_client_mock(self, mocker, status="SUCCESS", keypoint_id=111):
        client_mock = mocker.MagicMock()
        client_mock.return_value.wait_for_extraction.return_value = status
        client_mock.return_value.extract_keypoint_from_movie.return_value = keypoint_id
        client_mock.return_value.extract_keypoint_from_image.return_value = keypoint_id
        mocker.patch("encore_api_cli.commands.keypoint.get_client", client_mock)
        return client_mock


# TODO: refactor
def test_keypoint_extract_with_drawing(mocker):
    image_id = 111
    keypoint_id = 222

    client_mock = mocker.MagicMock()
    client_mock.return_value.wait_for_extraction.return_value = "SUCCESS"
    extract_keypoint_mock = client_mock.return_value.extract_keypoint_from_image
    extract_keypoint_mock.return_value = keypoint_id
    client_mock.return_value.draw_keypoint.return_value = 333
    client_mock.return_value.wait_for_drawing.return_value = ("SUCCESS", "url")
    client_mock.return_value.download.return_value = None
    mocker.patch("encore_api_cli.commands.keypoint.get_client", client_mock)
    mocker.patch("encore_api_cli.commands.draw.get_client", client_mock)

    runner = CliRunner()
    result = runner.invoke(
        cli, ["keypoint", "extract", "--image_id", image_id, "--with_drawing"]
    )

    assert client_mock.call_count == 2
    assert extract_keypoint_mock.call_count == 1
    assert extract_keypoint_mock.call_args == ((image_id,),)
    assert client_mock.return_value.draw_keypoint.call_count == 1
    assert client_mock.return_value.draw_keypoint.call_args == (
        (keypoint_id,),
        {"rule": None},
    )
    assert client_mock.return_value.download.call_count == 1

    assert result.exit_code == 0
