import click
from click_repl import repl
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

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

    # TODO: remove option
    # _remove_option(ctx, "--interactive")

    repl(
        ctx,
        prompt_kwargs={
            "message": message,
            "style": style,
            "history": FileHistory(get_app_dir() / ".repl-history"),
            "auto_suggest": AutoSuggestFromHistory(),
        },
    )


def _search_option_index(ctx: click.Context, target: str) -> int:
    for i, param in enumerate(ctx.command.params):
        if not isinstance(param, click.Option):
            continue
        for options in (param.opts, param.secondary_opts):
            for o in options:
                if o == target:
                    return i
    return -1


def _remove_option(ctx: click.Context, option: str) -> None:
    index = _search_option_index(ctx, option)
    if index != -1:
        ctx.command.params.pop(index)
