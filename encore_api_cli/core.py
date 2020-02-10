import click
from click_help_colors import HelpColorsMixin

from . import __version__
from .commands.analysis import cli as analysis
from .commands.analyze import cli as analyze
from .commands.configure import cli as configure
from .commands.download import cli as download
from .commands.draw import cli as draw
from .commands.drawing import cli as drawing
from .commands.extract import cli as extract
from .commands.image import cli as image
from .commands.keypoint import cli as keypoint
from .commands.movie import cli as movie
from .commands.upload import cli as upload
from .state import State, pass_state


class ColorsCommandCollection(HelpColorsMixin, click.CommandCollection):
    """A class that mixes HelpColorsMixin and CommandCollection."""

    def __init__(self, *args, **kwargs):
        super(ColorsCommandCollection, self).__init__(*args, **kwargs)


@click.command(
    cls=ColorsCommandCollection,
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
    help_options_color="cyan",
)
@click.version_option(
    version=click.style(__version__, fg="cyan"), message="%(prog)s version %(version)s"
)
@pass_state
@click.pass_context
def cli(ctx: click.Context, state: State) -> None:
    """Command Line Interface for AnyMotion API."""
    state.cli_name = str(ctx.find_root().info_name)

    # TODO: future warning
    # if state.cli_name != "amcli":
    #     warning = click.style("Warning", fg="yellow")
    #     old_cmd = click.style(state.cli_name, fg="cyan")
    #     new_cmd = click.style("amcli", fg="cyan")
    #     click.echo(
    #         f'{warning}: {old_cmd} command is deprecated. Use {new_cmd} command.',
    #         err=True,
    #     )
    #     click.echo()
