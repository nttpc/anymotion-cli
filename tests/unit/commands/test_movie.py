from textwrap import dedent

import pytest

from encore_api_cli.commands.movie import cli
from encore_sdk import RequestsError


def test_movie(runner):
    result = runner.invoke(cli, ["movie"])
    assert result.exit_code == 0


class TestMovieShow(object):
    def test_valid(self, mocker, runner):
        expected = dedent(
            """\

                {
                  "id": 1,
                  "name": "movie"
                }

            """
        )

        client_mock = self._get_client_mock(mocker)
        result = runner.invoke(cli, ["movie", "show", "1"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["movie", "show"], 'Error: Missing argument "MOVIE_ID"'),
            (["movie", "show", "not_value"], 'Error: Invalid value for "MOVIE_ID"'),
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
        result = runner.invoke(cli, ["movie", "show", "1"])

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
                "name": "movie",
            }
        mocker.patch("encore_api_cli.commands.movie.get_client", client_mock)
        return client_mock


class TestMovieList(object):
    def test_valid(self, mocker, runner):
        expected = dedent(
            """\

                [
                  {
                    "id": 1,
                    "name": "movie"
                  }
                ]

            """
        )

        client_mock = self._get_client_mock(mocker)

        result = runner.invoke(cli, ["movie", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected

    def test_with_spinner(self, mocker, monkeypatch, runner):
        monkeypatch.setenv("ANYMOTION_USE_SPINNER", "true")
        client_mock = self._get_client_mock(mocker)

        result = runner.invoke(cli, ["movie", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert "Retrieving..." in result.output

    def test_with_pager(self, mocker, runner):
        client_mock = self._get_client_mock(mocker, num_data=10)

        result = runner.invoke(cli, ["movie", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert '"id": 10' in result.output

    def test_with_error(self, mocker, runner):
        client_mock = self._get_client_mock(mocker, with_exception=True)
        result = runner.invoke(cli, ["movie", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert "Error" in result.output

    def _get_client_mock(self, mocker, num_data=1, with_exception=False):
        client_mock = mocker.MagicMock()
        if with_exception:
            client_mock.return_value.get_list_data.side_effect = RequestsError()
        else:
            data = [{"id": i + 1, "name": "movie"} for i in range(num_data)]
            client_mock.return_value.get_list_data.return_value = data
        mocker.patch("encore_api_cli.commands.movie.get_client", client_mock)
        return client_mock
