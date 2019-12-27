import click

from encore_api_cli.client import Client
from encore_api_cli.exceptions import SettingsValueError
from encore_api_cli.settings import Settings


def get_client(profile):
    settings = get_settings(profile)
    if not settings.is_ok():
        message = (
            "The credentials is invalid or not set. "
            'Run "encore configure" to set credentials.'
        )
        raise click.ClickException(message)
    return Client(
        settings.client_id,
        settings.client_secret,
        settings.url,
        interval=settings.interval,
        timeout=settings.timeout,
    )


def get_settings(profile, use_env=True):
    try:
        settings = Settings(profile, use_env=use_env)
    except SettingsValueError as e:
        raise click.ClickException(e)
    return settings
