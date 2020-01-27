import click
import pytest

from encore_api_cli.client import Client
from encore_api_cli.state import State
from encore_api_cli.utils import get_client, parse_rule


class TestGetClient(object):
    def test_is_okがTrueの場合clientが取得できること(self, mocker):
        settings_mock = mocker.MagicMock()
        settings_mock.return_value.is_ok.return_value = True
        settings_mock.return_value.client_id = "client_id"
        settings_mock.return_value.client_secret = "client_secret"
        settings_mock.return_value.base_url = "http://api.example.com/"
        settings_mock.return_value.interval = 10
        settings_mock.return_value.timeout = 600
        mocker.patch("encore_api_cli.utils.Settings", settings_mock)

        state = State()
        client = get_client(state)

        assert settings_mock.call_count == 1
        assert type(client) is Client

    def test_is_okがFalseの場合エラーが発生すること(self, mocker):
        settings_mock = mocker.MagicMock()
        settings_mock.return_value.is_ok.return_value = False
        mocker.patch("encore_api_cli.utils.Settings", settings_mock)

        state = State()
        with pytest.raises(click.ClickException):
            get_client(state)

        assert settings_mock.call_count == 1


class TestParseRule(object):
    @pytest.mark.parametrize("rule, expected", [(None, None), ("[1, 2]", [1, 2])])
    def test_valid(self, rule, expected):
        result = parse_rule(rule)
        assert result == expected

    @pytest.mark.parametrize("rule", ['"1"', "[1: 2]"])
    def test_invalid(self, rule):
        with pytest.raises(click.ClickException):
            parse_rule(rule)
