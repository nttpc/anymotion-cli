import click

from . import __version__
from .commands.analysis import cli as analysis
from .commands.analyze import cli as analyze
from .commands.configure import cli as configure
from .commands.draw import cli as draw
from .commands.image import cli as image
from .commands.keypoint import cli as keypoint
from .commands.movie import cli as movie
from .commands.upload import cli as upload


@click.command(cls=click.CommandCollection,
               sources=[
                   analysis, analyze, configure, draw, image, keypoint, movie,
                   upload
               ])
@click.version_option(version=__version__)
def cli():
    """Command Line Interface for AnyMotion API."""
    pass
