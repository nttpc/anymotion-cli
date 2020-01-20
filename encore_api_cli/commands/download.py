from pathlib import Path
from textwrap import dedent
from typing import Tuple
from urllib.parse import urlparse

import click

from encore_api_cli.options import common_options
from encore_api_cli.output import echo
from encore_api_cli.state import State, pass_state
from encore_api_cli.utils import color_path, get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.command()
@click.argument("drawing_id", type=int)
@click.option(
    "-o",
    "--out_dir",
    default=".",
    type=click.Path(exists=True),
    show_default=True,
    help="Path of directory to output drawn file.",
)
@common_options
@pass_state
@click.pass_context
def download(
    ctx: click.core.Context, state: State, drawing_id: int, out_dir: str
) -> None:
    """Download the drawn file."""
    c = get_client(state)
    status, url = c.wait_for_drawing(drawing_id)

    if status == "SUCCESS" and url is not None:
        is_ok, message, path = check_download(out_dir, url)
        if is_ok:
            c.download(url, path)
        else:
            prog = ctx.find_root().info_name
            message = message % {"prog": prog, "drawing_id": drawing_id}
        echo(message)
    else:
        echo("Unable to download because drawing failed.")


def check_download(out_dir: str, url: str) -> Tuple[bool, str, Path]:
    """Check if you want to overwrite before downloading.

    Returns:
        A tuple of is_ok, message, path.
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    path = Path(out_dir) / Path(str(urlparse(url).path)).name
    if path.exists():
        echo(f"File already exists: {color_path(path)}")
        if not click.confirm("Do you want to overwrite?"):
            message = dedent(
                """\
                    Skip download. To download it, run the following command.

                    "%(prog)s download %(drawing_id)s"
                """
            )
            return (False, message, path)

    message = f"Downloaded the file to {color_path(path)}."
    return (True, message, path)