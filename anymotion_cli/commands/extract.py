from typing import Optional

import click
from anymotion_sdk import RequestsError
from click_help_colors import HelpColorsGroup
from yaspin import yaspin

from ..exceptions import ClickException
from ..options import common_options
from ..output import echo, echo_success
from ..state import State, pass_state
from ..utils import color_id, get_client
from .download import download_options
from .draw import draw, draw_options


@click.group(cls=HelpColorsGroup, help_options_color="cyan")
def cli() -> None:  # noqa: D103
    pass


@cli.command(short_help="Extract keypoints from uploaded images or movies.")
@click.option("--movie-id", type=int)
@click.option("--image-id", type=int)
@click.option(
    "-d", "--with-drawing", is_flag=True, help="Drawing with the extracted keypoints.",
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
    movie_id: Optional[int],
    image_id: Optional[int],
    with_drawing: bool,
    **kwargs,
) -> None:
    """Extract keypoints from uploaded images or movies.

    Either "--image-id" or "--movie-id" is required.
    """
    if [movie_id, image_id].count(None) in [0, 2]:
        raise click.UsageError("Either '--movie-id' or '--image-id' is required")

    client = get_client(state)
    try:
        keypoint_id = client.extract_keypoint(
            data={"image_id": image_id, "movie_id": movie_id}
        )
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
