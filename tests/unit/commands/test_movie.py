from textwrap import dedent

import pytest
from click.testing import CliRunner

from encore_api_cli.commands.movie import cli


def test_movie():
    runner = CliRunner()
    result = runner.invoke(cli, ["movie"])

    assert result.exit_code == 0


class TestMovieShow(object):
    def test_valid(self, mocker):
        expected = dedent(
            """\

                {
                  "id": 1,
                  "name": "movie"
                }

            """
        )

        client_mock = self._get_client_mock(mocker)
        runner = CliRunner()
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
    def test_invalid_params(self, mocker, args, expected):
        client_mock = self._get_client_mock(mocker)
        runner = CliRunner()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert expected in result.output

    def _get_client_mock(self, mocker):
        client_mock = mocker.MagicMock()
        client_mock.return_value.get_one_data.return_value = {"id": 1, "name": "movie"}
        mocker.patch("encore_api_cli.commands.movie.get_client", client_mock)
        return client_mock


class TestMovieList(object):
    def test_valid(self, mocker):
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

        client_mock = mocker.MagicMock()
        client_mock.return_value.get_list_data.return_value = [
            {"id": 1, "name": "movie"}
        ]
        mocker.patch("encore_api_cli.commands.movie.get_client", client_mock)

        runner = CliRunner()
        result = runner.invoke(cli, ["movie", "list"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert result.output == expected
