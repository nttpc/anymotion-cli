import click

from . import __version__
from .click_custom import CustomCommandCollection
from .commands.analysis import cli as analysis
from .commands.analyze import cli as analyze
from .commands.compare import cli as compare
from .commands.comparison import cli as comparison
from .commands.configure import cli as configure
from .commands.download import cli as download
from .commands.draw import cli as draw
from .commands.drawing import cli as drawing
from .commands.extract import cli as extract
from .commands.image import cli as image
from .commands.keypoint import cli as keypoint
from .commands.movie import cli as movie
from .commands.upload import cli as upload
from .interactive import run_interactive_mode
from .options import profile_option
from .state import State, pass_state


@click.group(
    cls=CustomCommandCollection,
    sources=[
        analysis,
        analyze,
        compare,
        comparison,
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
    invoke_without_command=True,
    context_settings=dict(help_option_names=["-h", "--help"]),
    short_help="Command Line Interface for AnyMotion API.",
)
@click.option("--interactive", is_flag=True, help="Start interactive mode.")
@profile_option
@click.version_option(
    version=click.style(__version__, fg="cyan"), message="%(prog)s version %(version)s"
)
@pass_state
@click.pass_context
def cli(ctx: click.Context, state: State, interactive: bool) -> None:
    """Command Line Interface for AnyMotion API."""
    state.cli_name = str(ctx.find_root().info_name)

    if ctx.invoked_subcommand is None:
        if interactive:
            run_interactive_mode(ctx, state)
        else:
            click.echo(cli.get_help(ctx))
