import click

from encore_api_cli import __version__
from encore_api_cli.commands.analysis import cli as analysis
from encore_api_cli.commands.analyze import cli as analyze
from encore_api_cli.commands.configure import cli as configure
from encore_api_cli.commands.download import cli as download
from encore_api_cli.commands.draw import cli as draw
from encore_api_cli.commands.drawing import cli as drawing
from encore_api_cli.commands.extract import cli as extract
from encore_api_cli.commands.image import cli as image
from encore_api_cli.commands.keypoint import cli as keypoint
from encore_api_cli.commands.movie import cli as movie
from encore_api_cli.commands.upload import cli as upload


@click.command(
    cls=click.CommandCollection,
    sources=[
        analysis,
        analyze,
        configure,
        download,
        draw,
        drawing,
        extract,
        image,
        keypoint,
        movie,
        upload,
    ],  # type: ignore
)
@click.version_option(version=click.style(__version__, fg="cyan"))
def cli():
    """Command Line Interface for AnyMotion API."""
    pass
