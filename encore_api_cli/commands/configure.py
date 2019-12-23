import click

from encore_api_cli.config import Config


@click.group()
def cli():
    pass


@cli.group(invoke_without_command=True)
@click.option('--profile',
              default='default',
              help='Name of a named profile that you can configure.')
@click.pass_context
def configure(ctx, profile):
    """Configure your AnyMotion Credentials."""
    if ctx.invoked_subcommand is None:
        config = Config(profile)
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
