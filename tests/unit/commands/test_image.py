from textwrap import dedent

import pytest
from click.testing import CliRunner

from encore_api_cli.commands.image import cli


def test_image():
    runner = CliRunner()
    result = runner.invoke(cli, ["image"])

    assert result.exit_code == 0


class TestImageShow(object):
    def test_valid(self, mocker):
        expected = dedent(
            """\

                {
                  "id": 1,
                  "name": "image"
                }

            """
        )

        client_mock = self._get_client_mock(mocker)
        runner = CliRunner()
        result = runner.invoke(cli, ["image", "show", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["image", "show"], 'Error: Missing argument "IMAGE_ID"'),
            (["image", "show", "not_value"], 'Error: Invalid value for "IMAGE_ID"'),
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
        client_mock.return_value.get_one_data.return_value = {"id": 1, "name": "image"}
        mocker.patch("encore_api_cli.commands.image.get_client", client_mock)
        return client_mock


class TestImageList(object):
    def test_valid(self, mocker):
        expected = dedent(
            """\

                [
                  {
                    "id": 1,
                    "name": "image"
                  }
                ]

            """
        )

        client_mock = mocker.MagicMock()
        client_mock.return_value.get_list_data.return_value = [{"id": 1, "name": "image"}]
        mocker.patch("encore_api_cli.commands.image.get_client", client_mock)

        runner = CliRunner()
        result = runner.invoke(cli, ["image", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected
