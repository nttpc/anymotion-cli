import click

from encore_api_cli.client import Client
from encore_api_cli.exceptions import SettingsValueError
from encore_api_cli.settings import Settings
from encore_api_cli.state import State


def get_client(state: State) -> Client:
    settings = get_settings(state.profile)
    if not settings.is_ok():
        message = (
            "The credentials is invalid or not set. "
            'Run "encore configure" to set credentials.'
        )
        raise click.ClickException(message)

    return Client(
        str(settings.client_id),
        str(settings.client_secret),
        settings.url,
        settings.interval,
        settings.timeout,
        verbose=state.verbose,
    )


def get_settings(profile: str, use_env: bool = True) -> Settings:
    try:
        settings = Settings(profile, use_env=use_env)
    except SettingsValueError as e:
        raise click.ClickException(str(e))
    return settings
