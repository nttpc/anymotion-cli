import pytest
from encore_sdk.client import Client

from encore_api_cli.exceptions import ClickException, SettingsValueError
from encore_api_cli.state import State
from encore_api_cli.utils import get_client, get_settings, parse_rule


class TestGetClient(object):
    @pytest.mark.parametrize("verbose", [False, True])
    def test_valid_if_is_ok_True(self, mocker, verbose):
        settings_mock = mocker.MagicMock()
        settings_mock.return_value.is_ok.return_value = True
        settings_mock.return_value.client_id = "client_id"
        settings_mock.return_value.client_secret = "client_secret"
        settings_mock.return_value.api_url = "http://api.example.com/anymotion/v1/"
        settings_mock.return_value.interval = 10
        settings_mock.return_value.timeout = 600
        mocker.patch("encore_api_cli.utils.Settings", settings_mock)

        state = State()
        state.verbose = verbose
        client = get_client(state)

        assert settings_mock.call_count == 1
        assert type(client) is Client

    def test_error_occurs_if_is_ok_False(self, mocker):
        settings_mock = mocker.MagicMock()
        settings_mock.return_value.is_ok = False
        mocker.patch("encore_api_cli.utils.Settings", settings_mock)

        state = State()
        with pytest.raises(ClickException):
            get_client(state)

        assert settings_mock.call_count == 1

    def test_error_occurs_if_url_is_invalid(self, mocker):
        settings_mock = mocker.MagicMock()
        settings_mock.return_value.is_ok.return_value = True
        settings_mock.return_value.client_id = "client_id"
        settings_mock.return_value.client_secret = "client_secret"
        settings_mock.return_value.api_url = "http://api.example.com/"
        settings_mock.return_value.interval = 10
        settings_mock.return_value.timeout = 600
        mocker.patch("encore_api_cli.utils.Settings", settings_mock)

        state = State()
        with pytest.raises(ClickException):
            get_client(state)

        assert settings_mock.call_count == 1


class TestGetSettings(object):
    def test_valid(self, mocker):
        settings_mock = mocker.MagicMock()
        mocker.patch("encore_api_cli.utils.Settings", settings_mock)

        get_settings("default")

        assert settings_mock.call_count == 1

    def test_invalid(self, mocker):
        settings_mock = mocker.MagicMock(side_effect=SettingsValueError())
        mocker.patch("encore_api_cli.utils.Settings", settings_mock)

        with pytest.raises(ClickException):
            get_settings("default")

        assert settings_mock.call_count == 1


class TestParseRule(object):
    @pytest.mark.parametrize("rule, expected", [(None, None), ("[1, 2]", [1, 2])])
    def test_valid(self, rule, expected):
        result = parse_rule(rule)
        assert result == expected

    @pytest.mark.parametrize("rule", ['"1"', "[1: 2]"])
    def test_invalid(self, rule):
        with pytest.raises(ClickException):
            parse_rule(rule)
