from typing import Optional, Union

import click
from tabulate import tabulate

from ..exceptions import ClickException, SettingsValueError
from ..options import common_options
from ..output import echo, echo_warning
from ..settings import API_URL
from ..state import State, pass_state
from ..utils import get_settings


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.group(invoke_without_command=True)
@common_options
@pass_state
@click.pass_context
def configure(ctx: click.Context, state: State) -> None:
    """Configure your AnyMotion Credentials."""
    if ctx.invoked_subcommand is None:
        settings = get_settings(state.profile, use_env=False)

        api_url = click.prompt("AnyMotion API URL", default=settings.api_url)
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
            settings.write_config(api_url)
            settings.write_credentials(client_id, client_secret)
        except SettingsValueError as e:
            raise ClickException(str(e))


@configure.command()
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


@configure.command()
@common_options
@pass_state
def clear(state: State) -> None:
    """Clear the configuration."""
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
