import click
from tabulate import tabulate

from encore_api_cli.options import common_options
from encore_api_cli.state import pass_state
from encore_api_cli.utils import get_settings


@click.group()
def cli():
    pass


@cli.group(invoke_without_command=True)
@common_options
@pass_state
@click.pass_context
def configure(ctx, state):
    """Configure your AnyMotion Credentials."""
    if ctx.invoked_subcommand is None:
        settings = get_settings(state.profile, use_env=False)
        settings.url = click.prompt("AnyMotion API URL", default=settings.url)
        settings.client_id = click.prompt(
            "AnyMotion Client ID", default=settings.client_id
        )
        settings.client_secret = click.prompt(
            "AnyMotion Client Secret", default=settings.client_secret
        )
        settings.write()


@configure.command()
@common_options
@pass_state
def list(state):
    """Show the configuration you use."""
    settings = get_settings(state.profile)
    none = click.style("None", fg="yellow")

    def hidden_credentials(string):
        if string is None or len(string) == 0:
            return none
        else:
            return string[-4:].rjust(20, "*")

    client_id = hidden_credentials(settings.client_id)
    client_secret = hidden_credentials(settings.client_secret)
    table = tabulate(
        [
            ["profile", state.profile],
            ["api_url", settings.url],
            ["client_id", client_id],
            ["client_secret", client_secret],
            ["polling_interval", settings.interval],
            ["timeout", settings.timeout],
        ],
        headers=["Name", "Value"],
    )
    click.echo(table)

    if client_id == none or client_secret == none:
        message = "\nWarning: client_id and/or client_secret not set."
        click.secho(message, fg="yellow")
