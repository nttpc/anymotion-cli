import click

from ..utils import get_client


@click.group()
def cli():
    pass


@cli.group()
def movie():
    """Manege movies."""
    pass


@movie.command()
@click.option('--profile',
              default='default',
              help='Name of a named profile that you can configure.')
def list(profile):
    """Show movie list."""
    c = get_client(profile)
    c.show_list('movies')
