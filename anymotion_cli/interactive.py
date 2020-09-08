import click
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from .click_custom.repl import repl
from .config import get_app_dir
from .state import State


def run_interactive_mode(ctx: click.Context, state: State) -> None:
    """Run interactive mode."""
    click.echo("Start interactive mode.")
    click.echo(
        "You can use {help} command to explain usage.".format(
            help=click.style(":help", fg="cyan")
        )
    )
    click.echo()

    style = Style.from_dict({"profile": "gray"})
    message = [("class:cli_name", state.cli_name)]
    if state.profile != "default":
        message.append(("class:separator", " "))
        message.append(("class:profile", state.profile))
    message.append(("class:pound", "> "))

    repl(
        ctx,
        prompt_kwargs={
            "message": message,
            "style": style,
            "history": FileHistory(str(get_app_dir() / ".repl-history")),
            "auto_suggest": AutoSuggestFromHistory(),
        },
    )
