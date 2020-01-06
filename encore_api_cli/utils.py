import click

from encore_api_cli.client import Client
from encore_api_cli.exceptions import SettingsValueError
from encore_api_cli.settings import Settings
from encore_api_cli.state import State


def get_client(state: State) -> Client:
    """Get client from state."""
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
        settings.base_url,
        settings.interval,
        settings.timeout,
        verbose=state.verbose,
    )


def get_settings(profile: str, use_env: bool = True) -> Settings:
    """Get settings from profile."""
    try:
        settings = Settings(profile, use_env=use_env)
    except SettingsValueError as e:
        raise click.ClickException(str(e))
    return settings


def color_id(number: int) -> str:
    """Set color to ID."""
    return click.style(str(number), fg="cyan")


def color_path(path: str) -> str:
    """Set color to path."""
    return click.style(str(path), fg="blue")
