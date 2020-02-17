from textwrap import dedent

import pytest

from encore_api_cli.commands.image import cli
from encore_api_cli.sdk.exceptions import RequestsError


def test_image(runner):
    result = runner.invoke(cli, ["image"])
    assert result.exit_code == 0


class TestImageShow(object):
    def test_valid(self, mocker, runner):
        expected = dedent(
            """\

                {
                  "id": 1,
                  "name": "image"
                }

            """
        )

        client_mock = self._get_client_mock(mocker)
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
    def test_invalid_params(self, mocker, runner, args, expected):
        client_mock = self._get_client_mock(mocker)
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert expected in result.output

    def test_with_error(self, mocker, runner):
        client_mock = self._get_client_mock(mocker, with_exception=True)
        result = runner.invoke(cli, ["image", "show", "1"])

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
                "name": "image",
            }
        mocker.patch("encore_api_cli.commands.image.get_client", client_mock)
        return client_mock


class TestImageList(object):
    def test_valid(self, mocker, runner):
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

        client_mock = self._get_client_mock(mocker)

        result = runner.invoke(cli, ["image", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    def test_with_spinner(self, mocker, monkeypatch, runner):
        monkeypatch.setenv("ANYMOTION_USE_SPINNER", "true")
        client_mock = self._get_client_mock(mocker)

        result = runner.invoke(cli, ["image", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert "Retrieving..." in result.output

    def test_with_pager(self, mocker, runner):
        client_mock = self._get_client_mock(mocker, num_data=10)

        result = runner.invoke(cli, ["image", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert '"id": 10' in result.output

    def test_with_error(self, mocker, runner):
        client_mock = self._get_client_mock(mocker, with_exception=True)
        result = runner.invoke(cli, ["image", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert "Error" in result.output

    def _get_client_mock(self, mocker, num_data=1, with_exception=False):
        client_mock = mocker.MagicMock()
        if with_exception:
            client_mock.return_value.get_list_data.side_effect = RequestsError()
        else:
            data = [{"id": i + 1, "name": "image"} for i in range(num_data)]
            client_mock.return_value.get_list_data.return_value = data
        mocker.patch("encore_api_cli.commands.image.get_client", client_mock)
        return client_mock
