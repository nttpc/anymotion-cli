import click
import pytest

from encore_api_cli.client import Client
from encore_api_cli.state import State
from encore_api_cli.utils import get_client


def test_is_okがTrueの場合clientが取得できること(mocker):
    state = State()

    settings_mock = mocker.MagicMock()
    settings_mock.return_value.is_ok.return_value = True
    settings_mock.return_value.client_id = "client_id"
    settings_mock.return_value.client_secret = "client_secret"
    settings_mock.return_value.base_url = "http://api.example.com/"
    settings_mock.return_value.interval = 10
    settings_mock.return_value.timeout = 600
    mocker.patch("encore_api_cli.utils.Settings", settings_mock)

    client = get_client(state)

    assert settings_mock.call_count == 1
    assert type(client) is Client


def test_is_okがFalseの場合エラーが発生すること(mocker):
    state = State()

    settings_mock = mocker.MagicMock()
    settings_mock.return_value.is_ok.return_value = False
    mocker.patch("encore_api_cli.utils.Settings", settings_mock)

    with pytest.raises(click.ClickException):
        get_client(state)

    assert settings_mock.call_count == 1
