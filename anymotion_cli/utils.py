import json
import os
from distutils.util import strtobool
from pathlib import Path
from typing import List, Optional, Union

import click
from anymotion_sdk import Client, ClientValueError
from anymotion_sdk.session import HttpSession

from . import __version__
from .exceptions import ClickException, SettingsValueError
from .output import echo_request, echo_response, echo_warning
from .settings import Settings
from .state import State


def get_client(state: State) -> Client:
    """Get client from state."""
    settings = get_settings(state.profile)
    if not settings.is_ok:
        command = click.style(f"{state.cli_name} configure", fg="cyan")
        message = (
            "The credentials is invalid or not set. "
            f"Run {command} to set credentials."
        )
        raise ClickException(message)

    session = HttpSession()
    if hasattr(session, "user_agent"):
        session.user_agent = f"{state.cli_name}/{__version__}"

    try:
        client = Client(
            client_id=str(settings.client_id),
            client_secret=str(settings.client_secret),
            api_url=settings.api_url,
            interval=settings.interval,
            timeout=settings.timeout,
            session=session,
        )
    except ClientValueError as e:
        raise ClickException(str(e))

    if state.verbose:
        client.session.add_request_callback(echo_request)
        client.session.add_response_callback(echo_response)

    # TODO: refactor
    state.is_download = settings.is_download
    state.is_open = settings.is_open

    return client


# TODO: remove?
def get_settings(profile: str, use_env: bool = True) -> Settings:
    """Get settings from profile."""
    try:
        settings = Settings(profile, use_env=use_env)
    except SettingsValueError as e:
        raise ClickException(str(e))
    return settings


def parse_rule(rule: Optional[str]) -> Optional[Union[list, dict]]:
    """Convert string type analysis and drawing rules to list or dict type."""
    if rule is None:
        return rule

    try:
        rule = json.loads(rule)
    except json.decoder.JSONDecodeError:
        raise ClickException("Rule format is invalid. Must be in JSON format.")

    if not isinstance(rule, (list, dict)):
        message = "Rule format is invalid. Must be in list or object format."
        raise ClickException(message)

    return rule


def echo_invalid_option_warning(condition: str, target_options: List[str]) -> None:
    """Output warning message."""
    if len(target_options) == 0:
        return
    elif len(target_options) == 1:
        be, pronoun, s = "is", "This", ""
    else:
        be, pronoun, s = "are", "These", "s"
    opt_str = ", ".join([f"'{option}'" for option in target_options])
    message = (
        f"{opt_str} {be} only available when {condition}. "
        f"{pronoun} option{s} {be} ignored.\n"
    )
    echo_warning(message)


def color_id(number: int) -> str:
    """Set color to ID."""
    return click.style(str(number), fg="cyan")


def color_path(path: Union[str, Path]) -> str:
    """Set color to path."""
    return click.style(str(path), fg="blue")


def get_bool_env(key: str, default: bool) -> bool:
    """Get boolean environment variable."""
    str_env = os.getenv(key)
    if str_env:
        try:
            bool_env = bool(strtobool(str_env))
        except ValueError:
            bool_env = default
    else:
        bool_env = default
    return bool_env
