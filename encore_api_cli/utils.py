import json
import os
from distutils.util import strtobool
from pathlib import Path
from typing import Optional, Union

import click
from encore_sdk import Client, ClientValueError, RequestsError

from .exceptions import ClickException, SettingsValueError
from .output import echo_request, echo_response
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

    try:
        client = Client(
            client_id=str(settings.client_id),
            client_secret=str(settings.client_secret),
            api_url=settings.api_url,
            interval=settings.interval,
            timeout=settings.timeout,
        )
    except ClientValueError as e:
        raise ClickException(str(e))

    if state.verbose:
        client.session.add_request_callback(echo_request)
        client.session.add_response_callback(echo_response)

    return client


def get_name_from_drawing_id(client: Client, drawing_id: int) -> str:
    """Get image or movie name from drawing_id.

    Raises:
        RequestsError: HTTP request fails.
    """
    try:
        data = client.get_drawing(drawing_id)
        keypoint_id = data.get("keypoint")

        data = client.get_keypoint(keypoint_id)
        image_id = data.get("image")
        movie_id = data.get("movie")

        if image_id:
            data = client.get_image(image_id)
        elif movie_id:
            data = client.get_movie(movie_id)
        else:
            raise
    except RequestsError as e:
        raise ClickException(str(e))

    return data.get("name", "")


# TODO: remove?
def get_settings(profile: str, use_env: bool = True) -> Settings:
    """Get settings from profile."""
    try:
        settings = Settings(profile, use_env=use_env)
    except SettingsValueError as e:
        raise ClickException(str(e))
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
        message = "Rule format is invalid. Must be in list or object format."
        raise ClickException(message)

    return rule


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
