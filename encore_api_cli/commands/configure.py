import click

from encore_api_cli.config import Config
from encore_api_cli.options import common_options
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
        config = Config(state.profile)
        config.url = click.prompt('AnyMotion API URL', default=config.url)
        config.client_id = click.prompt('AnyMotion Client ID',
                                        default=config.client_id)
        config.client_secret = click.prompt('AnyMotion Client Secret',
                                            default=config.client_secret)
        config.update()


@configure.command()
def list():
    """Show the configuration you set."""
    config = Config()
    config.show()
