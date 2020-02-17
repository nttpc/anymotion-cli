from pathlib import Path
from textwrap import dedent
from typing import Optional, Tuple
from urllib.parse import urlparse

import click
from click_help_colors import HelpColorsGroup

from ..exceptions import ClickException
from ..options import common_options
from ..output import echo, echo_error
from encore_sdk import RequestsError
from ..state import State, pass_state
from ..utils import color_path, get_client


@click.group(cls=HelpColorsGroup, help_options_color="cyan")
def cli() -> None:  # noqa: D103
    pass


@cli.command(short_help="Download the drawn file.")
@click.argument("drawing_id", type=int)
@click.option(
    "-o",
    "--out-dir",
    default=".",
    type=click.Path(exists=True, file_okay=False),
    show_default=True,
    help="Path of directory to output drawn file.",
)
@common_options
@pass_state
def download(state: State, drawing_id: int, out_dir: str) -> None:
    """Download the drawn file."""
    client = get_client(state)

    try:
        status, url = client.wait_for_drawing(drawing_id)
        name = client.get_name_from_drawing_id(drawing_id)
    except RequestsError as e:
        raise ClickException(str(e))

    if status == "SUCCESS" and url is not None:
        is_ok, message, path = check_download(out_dir, url, name)
        if is_ok:
            try:
                client.download(url, path)
            except RequestsError as e:
                raise ClickException(str(e))
        else:
            message = message % {"prog": state.cli_name, "drawing_id": drawing_id}
        echo(message)
    else:
        echo_error("Unable to download because drawing failed.")


def check_download(
    out_dir: str, url: str, name: Optional[str] = None
) -> Tuple[bool, str, Path]:
    """Check if you want to overwrite before downloading.

    Returns:
        A tuple of is_ok, message, path.
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    if name:
        file_name = name + Path(str(urlparse(url).path)).suffix
    else:
        file_name = Path(str(urlparse(url).path)).name
    path = (Path(out_dir) / file_name).resolve()

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
