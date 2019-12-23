import click

from encore_api_cli.utils import get_client


@click.group()
def cli():
    pass


@cli.group()
def image():
    """Manege images."""
    pass


@image.command()
@click.option('--profile',
              default='default',
              help='Name of a named profile that you can configure.')
def list(profile):
    """Show image list."""
    c = get_client(profile)
    c.show_list('images')
