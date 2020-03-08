from pathlib import Path
from textwrap import dedent
from urllib.parse import urlparse
from typing import Callable, Optional

import click
from click_help_colors import HelpColorsGroup
from encore_sdk import RequestsError
from yaspin import yaspin

from ..exceptions import ClickException
from ..options import common_options
from ..output import echo
from ..state import State, pass_state
from ..utils import color_path, get_client


def download_options(f: Callable) -> Callable:
    """Set download options."""
    f = click.option(
        "--open/--no-open",
        "is_open",
        default=None,
        help="Whether to open downloaded the file.",
    )(f)
    f = click.option(
        "--force", is_flag=True, help="If the file exists, download it by overwriting.",
    )(f)
    f = click.option(
        "-o",
        "--out-dir",
        default=".",
        type=click.Path(exists=True, file_okay=False),
        show_default=True,
        help="Path of directory to output drawn file.",
    )(f)
    return f


@click.group(cls=HelpColorsGroup, help_options_color="cyan")
def cli() -> None:  # noqa: D103
    pass


@cli.command(short_help="Download the drawn file.")
@click.argument("drawing_id", type=int)
@download_options
@common_options
@pass_state
def download(
    state: State, drawing_id: int, out_dir: str, force: bool, is_open: Optional[bool]
) -> None:
    """Download the drawn file."""
    client = get_client(state)

    try:
        data = client.get_drawing(drawing_id)
    except RequestsError as e:
        raise ClickException(str(e))

    status = data.get("execStatus")
    url = data.get("drawingUrl")
    keypoint_id = data.get("keypoint")

    if status != "SUCCESS" or url is None:
        raise ClickException("Unable to download because drawing failed.")

    try:
        name = _get_name_from_keypoint_id(client, keypoint_id)
    except RequestsError as e:
        raise ClickException(str(e))

    if name:
        file_name = name + Path(str(urlparse(url).path)).suffix
    else:
        file_name = Path(str(urlparse(url).path)).name
    path = (Path(out_dir) / file_name).resolve()

    if force or not _is_skip(path):
        try:
            if state.use_spinner:
                with yaspin(text="Downloading..."):
                    client.download(drawing_id, path, exist_ok=True)
            else:
                client.download(drawing_id, path, exist_ok=True)
        except RequestsError as e:
            raise ClickException(str(e))

        echo(f"Downloaded the file to {color_path(path)}.")

        if is_open is None:
            is_open = click.confirm("Open the Downloaded file?")
        if is_open:
            click.launch(str(path))
    else:
        message = dedent(
            f"""\
            Skip download. To download it, run the following command.

            "{state.cli_name} download {drawing_id}"
            """
        )
        echo(message)


def _get_name_from_keypoint_id(client, keypoint_id: int) -> str:
    data = client.get_keypoint(keypoint_id)
    image_id = data.get("image")
    movie_id = data.get("movie")

    if image_id:
        data = client.get_image(image_id)
    elif movie_id:
        data = client.get_movie(movie_id)
    else:
        return ""

    return data.get("name", "")


def _is_skip(path: Path):
    if path.exists():
        echo(f"File already exists: {color_path(path)}")
        if not click.confirm("Do you want to overwrite?"):
            return True
    return False
