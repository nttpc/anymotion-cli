import click

from encore_api_cli import __version__
from encore_api_cli.commands.analysis import cli as analysis
from encore_api_cli.commands.analyze import cli as analyze
from encore_api_cli.commands.configure import cli as configure
from encore_api_cli.commands.draw import cli as draw
from encore_api_cli.commands.image import cli as image
from encore_api_cli.commands.keypoint import cli as keypoint
from encore_api_cli.commands.movie import cli as movie
from encore_api_cli.commands.upload import cli as upload


@click.command(cls=click.CommandCollection,
               sources=[
                   analysis, analyze, configure, draw, image, keypoint, movie,
                   upload
               ])
@click.version_option(version=__version__)
def cli():
    """Command Line Interface for AnyMotion API."""
    pass
