from pathlib import Path
from textwrap import dedent
from urllib.parse import urlparse

import click
from click_help_colors import HelpColorsGroup
from encore_sdk import RequestsError
from yaspin import yaspin

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


@click.group(cls=HelpColorsGroup, help_options_color="cyan")
def cli() -> None:  # noqa: D103
    pass


@cli.command(short_help="Download the drawn file.")
@click.argument("drawing_id", type=int)
@click.option(
    "-o",
    "--out",
    default=".",
    callback=validate_path,
    show_default=True,
    help="Path of file or directory to output drawn file.",
)
# @click.option(
#     "--overwrite", is_flag=True, help="If the file exists, overwrite it.",
# )
@common_options
@pass_state
def download(state: State, drawing_id: int, out: Path) -> None:
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

    url_path = Path(str(urlparse(url).path))
    if out.is_dir():
        try:
            name = _get_name_from_keypoint_id(client, keypoint_id)
        except RequestsError as e:
            raise ClickException(str(e))

        if name:
            file_name = name + url_path.suffix
        else:
            file_name = url_path.name
        path = out / file_name
    else:
        path = out
        if path.suffix.lower() != url_path.suffix.lower():
            echo_warning(f'"{path.suffix}" is not a valid extension.')
            expected_name = path.with_suffix(url_path.suffix).name
            if click.confirm(f'Change from "{path.name}" to "{expected_name}"?'):
                path = path.with_suffix(url_path.suffix)

    # if overwrite or not _is_skip(path):
    if not _is_skip(path):
        try:
            if state.use_spinner:
                with yaspin(text="Downloading..."):
                    client.download(drawing_id, path, exist_ok=True)
            else:
                client.download(drawing_id, path, exist_ok=True)
        except RequestsError as e:
            raise ClickException(str(e))

        echo(f"Downloaded the file to {color_path(path)}.")
        # click.launch(str(path))
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
