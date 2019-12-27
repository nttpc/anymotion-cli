import click
from tabulate import tabulate

from encore_api_cli.options import common_options
from encore_api_cli.settings import Settings
from encore_api_cli.state import pass_state


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
        settings = Settings(state.profile)
        settings.url = click.prompt('AnyMotion API URL', default=settings.url)
        settings.client_id = click.prompt('AnyMotion Client ID',
                                          default=settings.client_id)
        settings.client_secret = click.prompt('AnyMotion Client Secret',
                                              default=settings.client_secret)
        settings.write()


@configure.command()
@common_options
@pass_state
def list(state):
    """Show the configuration you use."""
    settings = Settings(state.profile)

    def hidden_credentials(string):
        if string is None:
            message = 'Warning: client_id and/or client_secret not set.'
            click.echo(click.style(message, fg='yellow'))
            click.echo()
            return 'None'
        else:
            return string[-4:].rjust(20, '*')

    client_id = hidden_credentials(settings.client_id)
    client_secret = hidden_credentials(settings.client_secret)
    table = tabulate(
        [['profile', state.profile], ['api_url', settings.url],
         ['client_id', client_id], ['client_secret', client_secret],
         ['polling_interval', settings.interval],
         ['timeout', settings.timeout]],
        headers=['Name', 'Value'])
    click.echo(table)
