import click
import pytest

from encore_api_cli.client import Client
from encore_api_cli.utils import get_client


def test_configのis_okがTrueの場合clientが取得できること(mocker):
    profile = 'default'

    config_mock = mocker.MagicMock()
    config_mock.return_value.is_ok = True
    mocker.patch('encore_api_cli.utils.Config', config_mock)

    client = get_client(profile)

    assert config_mock.call_count == 1
    assert type(client) is Client


def test_configのis_okがFalseの場合エラーが発生すること(mocker):
    profile = 'default'

    config_mock = mocker.MagicMock()
    config_mock.return_value.is_ok = False
    mocker.patch('encore_api_cli.utils.Config', config_mock)

    with pytest.raises(click.ClickException):
        get_client(profile)

    assert config_mock.call_count == 1
