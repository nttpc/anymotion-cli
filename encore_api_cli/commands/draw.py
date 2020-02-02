import io
from typing import Callable, Optional

import click
from yaspin import yaspin

from encore_api_cli.commands.download import check_download
from encore_api_cli.options import common_options
from encore_api_cli.output import echo, echo_success
from encore_api_cli.state import State, pass_state
from encore_api_cli.utils import color_id, get_client, parse_rule


def draw_options(f: Callable) -> Callable:
    """Set draw options."""
    f = click.option("--no-download", is_flag=True, help="Disable download.")(f)
    f = click.option("--rule", "rule_str", help="Drawing rules in JSON format.")(f)
    f = click.option(
        "--rule-file", type=click.File(), help="Drawing rules file in JSON format."
    )(f)
    f = click.option(
        "-o",
        "--out-dir",
        default=".",
        type=click.Path(),
        show_default=True,
        help="Path of directory to output drawn file.",
    )(f)
    return f


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.command()
@click.argument("keypoint_id", type=int)
@draw_options
@common_options
@pass_state
@click.pass_context
def draw(
    ctx: click.core.Context,
    state: State,
    keypoint_id: int,
    out_dir: str,
    rule_str: Optional[str],
    rule_file: Optional[io.TextIOWrapper],
    no_download: bool,
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
    drawing_id = client.draw_keypoint(keypoint_id, rule=rule)

    echo(f"Drawing started. (drawing id: {color_id(drawing_id)})")
    if state.use_spinner:
        with yaspin(text="Processing..."):
            status, url = client.wait_for_drawing(drawing_id)
    else:
        status, url = client.wait_for_drawing(drawing_id)

    if status == "SUCCESS" and url is not None:
        echo_success("Drawing is complete.")
        if no_download:
            return

        is_ok, message, path = check_download(out_dir, url)
        if is_ok:
            client.download(url, path)
        else:
            prog = ctx.find_root().info_name
            message = message % {"prog": prog, "drawing_id": drawing_id}
        echo(message)
    elif status == "TIMEOUT":
        echo("Drawing is timed out.")
    else:
        echo("Drawing failed.")
