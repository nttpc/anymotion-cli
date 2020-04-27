import io
from textwrap import dedent
from typing import Callable, Optional

import click
from anymotion_sdk import RequestsError
from click_help_colors import HelpColorsGroup
from yaspin import yaspin

from ..exceptions import ClickException
from ..options import common_options
from ..output import echo, echo_success
from ..state import State, pass_state
from ..utils import color_id, get_client, parse_rule
from .download import download, download_options


def draw_options(f: Callable) -> Callable:
    """Set draw options."""
    f = click.option(
        "--download/--no-download",
        "is_download",
        default=None,
        help=(
            "Whether to download the drawn file. "
            'If you change the default value, run "configure set is_download".'
        ),
    )(f)
    f = click.option(
        "--rule-file", type=click.File(), help="Drawing rules file in JSON format."
    )(f)
    f = click.option("--rule", "rule_str", help="Drawing rules in JSON format.")(f)
    return f


@click.group(cls=HelpColorsGroup, help_options_color="cyan")
def cli() -> None:  # noqa: D103
    pass


@cli.command(short_help="Draw points and/or lines on uploaded movie or image.")
@click.argument("keypoint_id", type=int)
@draw_options
@download_options
@common_options
@pass_state
@click.pass_context
def draw(
    ctx: click.Context,
    state: State,
    keypoint_id: int,
    rule_str: Optional[str],
    rule_file: Optional[io.TextIOWrapper],
    is_download: Optional[bool],
    **kwargs,
) -> None:
    """Draw points and/or lines on uploaded movie or image."""
    if rule_str is not None and rule_file is not None:
        raise click.UsageError(
            '"rule" and "rule-file" options cannot be used at the same time.'
        )

    rule = None
    if rule_str is not None:
        rule = parse_rule(rule_str)
    elif rule_file is not None:
        rule = parse_rule(rule_file.read())

    client = get_client(state)

    try:
        drawing_id = client.draw_keypoint(keypoint_id, rule=rule)
        echo(f"Drawing started. (drawing id: {color_id(drawing_id)})")

        if state.use_spinner:
            with yaspin(text="Processing..."):
                response = client.wait_for_drawing(drawing_id)
        else:
            response = client.wait_for_drawing(drawing_id)
    except RequestsError as e:
        raise ClickException(str(e))

    if response.status == "SUCCESS":
        echo_success("Drawing is complete.")
    elif response.status == "TIMEOUT":
        raise ClickException("Drawing is timed out.")
    else:
        raise ClickException("Drawing failed.")

    echo()
    if is_download is None:
        is_download = state.is_download
    if is_download is None:
        is_download = click.confirm("Download the drawn file?")
    if is_download:
        ctx.invoke(download, drawing_id=drawing_id, **kwargs)
    else:
        message = dedent(
            f"""\
            Skip download. To download it, run the following command.

            "{state.cli_name} download {drawing_id}"
            """
        )
        echo(message)
