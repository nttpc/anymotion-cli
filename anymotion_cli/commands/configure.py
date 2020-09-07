from typing import Any, Optional, Union

import click
from tabulate import tabulate

from ..click_custom import CustomGroup
from ..exceptions import ClickException, SettingsValueError
from ..options import common_options
from ..output import echo, echo_warning
from ..settings import API_URL
from ..state import State, pass_state
from ..utils import get_settings


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.group(
    cls=CustomGroup,
    invoke_without_command=True,
    help_options_color="cyan",
    short_help="Configure your AnyMotion Credentials.",
)
@common_options
@pass_state
@click.pass_context
def configure(ctx: click.Context, state: State) -> None:
    """Configure your AnyMotion Credentials."""
    if ctx.invoked_subcommand is None:
        settings = get_settings(state.profile, use_env=False)

        client_id = click.prompt(
            "AnyMotion Client ID",
            default=make_hidden(settings.client_id),
            hide_input=True,
        )
        client_secret = click.prompt(
            "AnyMotion Client Secret",
            default=make_hidden(settings.client_secret),
            hide_input=True,
        )

        if isinstance(client_id, HiddenCredential):
            client_id = client_id.value
        if isinstance(client_secret, HiddenCredential):
            client_secret = client_secret.value

        try:
            settings.write_credentials(client_id, client_secret)
        except SettingsValueError as e:
            raise ClickException(str(e))


@configure.command(short_help="Show the configuration you use.")
@common_options
@pass_state
def list(state: State) -> None:
    """Show the configuration you use."""
    settings = get_settings(state.profile)

    none = click.style("None", fg="yellow")
    client_id = make_hidden(settings.client_id, none)
    client_secret = make_hidden(settings.client_secret, none)

    table = tabulate(
        [
            ["profile", state.profile],
            ["api_url", settings.api_url],
            ["client_id", client_id],
            ["client_secret", client_secret],
            ["polling_interval", settings.interval],
            ["timeout", settings.timeout],
        ],
        headers=["Name", "Value"],
    )
    echo(table)

    if client_id == none or client_secret == none:
        echo()
        echo_warning("client_id and/or client_secret not set.")


@configure.command(short_help="Get a configuration value from the file.")
@click.argument(
    "key",
    type=click.Choice(
        [
            "client_id",
            "client_secret",
            "api_url",
            "polling_interval",
            "timeout",
            "is_download",
            "is_open",
        ],
        case_sensitive=False,
    ),
)
@common_options
@pass_state
def get(state: State, key: str) -> None:
    """Get a configuration value from the file."""
    settings = get_settings(state.profile, use_env=False)

    if key == "client_id":
        echo(settings.client_id)
    elif key == "client_secret":
        echo(settings.client_secret)
    elif key == "api_url":
        echo(settings.api_url)
    elif key == "polling_interval":
        echo(_to_str(settings.interval))
    elif key == "timeout":
        echo(_to_str(settings.timeout))
    elif key == "is_download":
        echo(_to_str(settings.is_download))
    elif key == "is_open":
        echo(_to_str(settings.is_open))


@configure.command(short_help="Set a configuration value in the file.")
@click.argument(
    "key", type=click.Choice(["client_id", "client_secret"], case_sensitive=False)
)
@click.argument("value")
@common_options
@pass_state
def set(state: State, key: str, value: str) -> None:
    """Set a configuration value in the file."""
    settings = get_settings(state.profile, use_env=False)

    if key == "client_id":
        client_secret = _to_str(settings.client_secret)
        settings.write_credentials(value, client_secret)
    elif key == "client_secret":
        client_id = _to_str(settings.client_id)
        settings.write_credentials(client_id, value)


@configure.command(short_help="Clear the configuration value from the file.")
@common_options
@pass_state
def clear(state: State) -> None:
    """Clear a configuration value from the file."""
    settings = get_settings(state.profile)
    settings.write_config(API_URL)
    settings.write_credentials("", "")


class HiddenCredential(str):
    """Make hidden the credentials value.

    Examples:
        >>> x = HiddenCredential("abcdefghij")
        >>> str(x)
        ****************ghij
        >>> x.value
        abcdefghij
    """

    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return self.value[-4:].rjust(20, "*")


def make_hidden(
    value: Optional[str], default: Optional[str] = None
) -> Optional[Union[str, HiddenCredential]]:
    """Get hidden value."""
    if value:
        return HiddenCredential(value)
    else:
        return default


def _to_str(value: Any) -> str:
    if value is None:
        return ""
    else:
        return str(value)
