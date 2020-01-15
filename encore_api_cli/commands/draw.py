from typing import Callable, Optional

import click

from encore_api_cli.commands.download import check_download
from encore_api_cli.options import common_options
from encore_api_cli.output import write_message, write_success
from encore_api_cli.state import State, pass_state
from encore_api_cli.utils import color_id, get_client, parse_rule


def draw_options(f: Callable) -> Callable:
    """Set draw options."""
    f = click.option("--no-download", is_flag=True, help="Disable download.")(f)
    f = click.option("--rule", help="Drawing rules in JSON format.")(f)
    f = click.option(
        "-o",
        "--out_dir",
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
    rule: Optional[str],
    no_download: bool,
) -> None:
    """Draw keypoints on uploaded movie or image."""
    c = get_client(state)
    drawing_id = c.draw_keypoint(keypoint_id, rule=parse_rule(rule))
    write_message(f"Drawing started. (drawing_id: {color_id(drawing_id)})")

    status, url = c.wait_for_drawing(drawing_id)
    if status == "SUCCESS" and url is not None:
        write_success("Drawing is complete.")
        if no_download:
            return

        is_ok, message, path = check_download(out_dir, url)
        if is_ok:
            c.download(url, path)
        else:
            prog = ctx.find_root().info_name
            message = message % {"prog": prog, "drawing_id": drawing_id}
        write_message(message)
    elif status == "TIMEOUT":
        write_message("Drawing is timed out.")
    else:
        write_message("Drawing failed.")
