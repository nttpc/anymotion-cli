from pathlib import Path
from typing import Optional

import click
from anymotion_sdk import RequestsError
from yaspin import yaspin

from ..click_custom import CustomCommand
from ..exceptions import ClickException
from ..options import common_options
from ..output import echo, echo_success
from ..state import State, pass_state
from ..utils import color_id, get_client
from .download import download_options
from .draw import draw, draw_options
from .upload import upload


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.command(
    cls=CustomCommand,
    help_options_color="cyan",
    short_help="Extract keypoints from uploaded images or movies.",
)
@click.option("--image-id", type=int, help="Uploaded image ID.")
@click.option("--movie-id", type=int, help="Uploaded movie ID.")
@click.option(
    "--path",
    type=click.Path(exists=True, dir_okay=False),
    help="The path of the movie or image file to extract.",
)
@click.option(
    "-d",
    "--with-drawing",
    is_flag=True,
    help="Drawing with the extracted keypoints.",
)
# TODO: remove download and draw option
@draw_options
@download_options
@common_options
@pass_state
@click.pass_context
def extract(
    ctx: click.Context,
    state: State,
    image_id: Optional[int],
    movie_id: Optional[int],
    path: Path,
    with_drawing: bool,
    **kwargs,
) -> None:
    """Extract keypoints from image or movie.

    Either '--image-id' or '--movie-id' or '--path' is required.
    """
    # Because path defaults to the current directory, not to None.
    is_path = not path.is_dir()

    if [bool(image_id), bool(movie_id), is_path].count(True) != 1:
        raise click.UsageError(
            "Either '--image-id' or '--movie-id' or '--path' is required"
        )

    client = get_client(state)

    result = None
    if is_path:
        result = ctx.invoke(upload, path=path)._asdict()
        echo()
    data = result or {"image_id": image_id, "movie_id": movie_id}

    try:
        keypoint_id = client.extract_keypoint(data=data)
        echo(f"Keypoint extraction started. (keypoint id: {color_id(keypoint_id)})")

        if state.use_spinner:
            with yaspin(text="Processing..."):
                response = client.wait_for_extraction(keypoint_id)
        else:
            response = client.wait_for_extraction(keypoint_id)
    except RequestsError as e:
        raise ClickException(str(e))

    if response.status == "SUCCESS":
        echo_success("Keypoint extraction is complete.")
    elif response.status == "TIMEOUT":
        raise ClickException("Keypoint extraction is timed out.")
    else:
        raise ClickException(f"Keypoint extraction failed.\n{response.failure_detail}")

    if with_drawing:
        echo()
        ctx.invoke(draw, keypoint_id=keypoint_id, **kwargs)
