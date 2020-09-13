from pathlib import Path
from textwrap import dedent
from typing import Callable, List, Optional
from urllib.parse import urlparse

import click
from anymotion_sdk import RequestsError
from yaspin import yaspin

from ..click_custom import CustomCommand
from ..exceptions import ClickException
from ..options import common_options
from ..output import echo, echo_warning
from ..state import State, pass_state
from ..utils import color_path, get_client


def validate_path(ctx, param, value):
    """Validate path."""
    path = Path(value)
    if path.parent.exists() is False:
        raise click.BadParameter(f'File "{path}" is not writable.')
    return path.expanduser().resolve()


def download_options(f: Callable) -> Callable:
    """Set download options."""
    f = click.option(
        "--open/--no-open",
        "is_open",
        default=None,
        help="Whether to open downloaded the file.",
    )(f)
    f = click.option(
        "--force",
        is_flag=True,
        help="If the file exists, download it by overwriting.",
    )(f)
    f = click.option(
        "-o",
        "--out",
        default=Path(),
        callback=validate_path,
        show_default=True,
        metavar="PATH",
        help="Path of file or directory to output drawn file.",
    )(f)
    return f


def check_download_options(args: List[str]) -> List[str]:
    """Check to see if download options are being used.

    Returns:
        A list of using option names.
    """
    used_options = set(args) & set(["-o", "--out", "--force", "--open", "--no-open"])
    return list(used_options)


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.command(
    cls=CustomCommand, help_options_color="cyan", short_help="Download the drawn file."
)
@click.argument("drawing_id", type=int)
@download_options
@common_options
@pass_state
def download(
    state: State, drawing_id: int, out: Path, force: bool, is_open: Optional[bool]
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
    comparison_id = data.get("comparison")

    if status != "SUCCESS" or url is None:
        raise ClickException("Unable to download because drawing failed.")

    url_path = Path(str(urlparse(url).path))
    if out.is_dir():
        try:
            if keypoint_id:
                name = _get_name_from_keypoint_id(client, keypoint_id)
            elif comparison_id:
                name = _get_name_from_comparison_id(client, comparison_id)
            else:
                name = ""
        except RequestsError as e:
            raise ClickException(str(e))

        if name:
            file_name = name + url_path.suffix
        else:
            file_name = url_path.name
        out /= file_name

    if out.suffix.lower() != url_path.suffix.lower():
        echo_warning(f'"{out.suffix}" is not a valid extension.')
        expected_name = out.with_suffix(url_path.suffix).name
        if click.confirm(f'Change output path from "{out.name}" to "{expected_name}"?'):
            out = out.with_suffix(url_path.suffix)

    if force or not _is_skip(out):
        try:
            if state.use_spinner:
                with yaspin(text="Downloading..."):
                    client.download(drawing_id, out, exist_ok=True)
            else:
                client.download(drawing_id, out, exist_ok=True)
        except RequestsError as e:
            raise ClickException(str(e))

        echo(f"Downloaded the file to {color_path(out)}.")

        if is_open is None:
            is_open = state.is_open
        if is_open is None:
            is_open = click.confirm("Open the Downloaded file?")
        if is_open:
            click.launch(str(out))
    else:
        message = dedent(
            f"""\
            Skip download. To download it, run the following command.

            "{state.cli_name} download {drawing_id}"
            """
        )
        echo(message)


def _get_name_from_keypoint_id(client, keypoint_id: Optional[int]) -> str:
    if keypoint_id is None:
        return ""

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


def _get_name_from_comparison_id(client, comparison_id: Optional[int]) -> str:
    if comparison_id is None:
        return ""

    data = client.get_comparison(comparison_id)
    target_id = data.get("target")
    source_id = data.get("source")

    target_name = _get_name_from_keypoint_id(client, target_id)
    source_name = _get_name_from_keypoint_id(client, source_id)

    if target_name and source_name:
        return f"{target_name}_{source_name}"
    else:
        return ""


def _is_skip(path: Path):
    if path.exists():
        echo(f"File already exists: {color_path(path)}")
        if not click.confirm("Do you want to overwrite?"):
            return True
    return False
