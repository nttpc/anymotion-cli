from typing import Optional

import click
from tabulate import tabulate

from ..options import common_options
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
        base_url = click.prompt("AnyMotion API URL", default=settings.base_url)
        client_id = click.prompt("AnyMotion Client ID", default=settings.client_id)
        client_secret = click.prompt(
            "AnyMotion Client Secret", default=settings.client_secret
        )
        settings.write_config(base_url)
        settings.write_credentials(client_id, client_secret)


@configure.command()
@common_options
@pass_state
def list(state: State) -> None:
    """Show the configuration you use."""
    settings = get_settings(state.profile)
    none = click.style("None", fg="yellow")

    def hidden_credentials(string: Optional[str]) -> str:
        if string is None or len(string) == 0:
            return none
        else:
            return string[-4:].rjust(20, "*")

    client_id = hidden_credentials(settings.client_id)
    client_secret = hidden_credentials(settings.client_secret)
    table = tabulate(
        [
            ["profile", state.profile],
            ["api_url", settings.base_url],
            ["client_id", client_id],
            ["client_secret", client_secret],
            ["polling_interval", settings.interval],
            ["timeout", settings.timeout],
        ],
        headers=["Name", "Value"],
    )
    click.echo(table)

    if client_id == none or client_secret == none:
        # TODO: use echo_warning
        message = "\nWarning: client_id and/or client_secret not set."
        click.secho(message, fg="yellow")
