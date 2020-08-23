import click
from click_help_colors import HelpColorsMixin
from click_repl import repl
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from . import __version__
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
from .config import get_app_dir
from .options import profile_option
from .state import State, pass_state


class ColorsCommandCollection(HelpColorsMixin, click.CommandCollection):
    """A class that mixes HelpColorsMixin and CommandCollection."""

    def __init__(self, *args, **kwargs):
        super(ColorsCommandCollection, self).__init__(*args, **kwargs)


@click.group(
    cls=ColorsCommandCollection,
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
            _run_interactive_mode(state)
        else:
            click.echo(cli.get_help(ctx))


def _run_interactive_mode(state):
    click.echo("Start interactive mode.")
    click.echo(
        "You can use the internal {help} command to explain usage.".format(
            help=click.style(":help", fg="cyan")
        )
    )
    click.echo()

    style = Style.from_dict({"profile": "gray"})
    message = [
        ("class:cli_name", state.cli_name),
        ("class:separator", " "),
        ("class:profile", state.profile),
        ("class:pound", "> "),
    ]

    repl(
        click.get_current_context(),
        prompt_kwargs={
            "message": message,
            "style": style,
            "history": FileHistory(get_app_dir() / ".repl-history"),
        },
    )
