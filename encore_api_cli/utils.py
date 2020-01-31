import json
from pathlib import Path
from typing import Optional, Union

import click
import pkg_resources

from encore_api_cli.exceptions import ClickException, SettingsValueError
from encore_api_cli.output import echo_request, echo_response, spin
from encore_api_cli.sdk.client import Client
from encore_api_cli.settings import Settings
from encore_api_cli.state import State


def get_client(state: State) -> Client:
    """Get client from state."""
    settings = get_settings(state.profile)
    if not settings.is_ok():
        # FIXME: use prog instead of "encore"
        message = (
            "The credentials is invalid or not set. "
            'Run "encore configure" to set credentials.'
        )
        raise click.ClickException(message)

    return Client(
        str(settings.client_id),
        str(settings.client_secret),
        base_url=settings.base_url,
        interval=settings.interval,
        timeout=settings.timeout,
        verbose=state.verbose,
        echo_request=echo_request,
        echo_response=echo_response,
        echo_spin=spin,
    )


def get_settings(profile: str, use_env: bool = True) -> Settings:
    """Get settings from profile."""
    try:
        settings = Settings(profile, use_env=use_env)
    except SettingsValueError as e:
        raise click.ClickException(str(e))
    return settings


def parse_rule(rule: Optional[str]) -> Optional[list]:
    """Convert string type analysis and drawing rules to list type."""
    if rule is None:
        return rule

    try:
        rule = json.loads(rule)
    except json.decoder.JSONDecodeError:
        raise ClickException("Rule format is invalid. Must be in JSON format.")

    if not isinstance(rule, (list, dict)):
        raise ClickException(
            "Rule format is invalid. Must be in list or object format."
        )

    return rule


def color_id(number: int) -> str:
    """Set color to ID."""
    return click.style(str(number), fg="cyan")


def color_path(path: Union[str, Path]) -> str:
    """Set color to path."""
    return click.style(str(path), fg="blue")


def get_version():
    """Get package version."""
    return pkg_resources.get_distribution("encore_api_cli").version
