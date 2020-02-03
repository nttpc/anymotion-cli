import io
from typing import Optional

import click
from yaspin import yaspin

from ..options import common_options
from ..output import echo, echo_success
from ..sdk.exceptions import RequestsError
from ..state import State, pass_state
from ..utils import color_id, get_client
from .draw import draw, draw_options


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.command()
@click.option(
    "--movie-id",
    type=int,
    help='ID of movie to extrat, either "--movie-id" or "--image-id" is required.',
)
@click.option(
    "--image-id",
    type=int,
    help='ID of image to extrat, either "--movie-id" or "--image-id" is required.',
)
@click.option(
    "-d",
    "--with-drawing",
    is_flag=True,
    help="Flag for whether to draw at the same time.",
)
@draw_options
@common_options
@pass_state
@click.pass_context
def extract(
    ctx: click.Context,
    state: State,
    movie_id: Optional[int],
    image_id: Optional[int],
    with_drawing: bool,
    out_dir: str,
    rule_str: Optional[str],
    rule_file: Optional[io.TextIOWrapper],
    no_download: bool,
) -> None:
    """Extract keypoints from uploaded images or movies."""
    if [movie_id, image_id].count(None) in [0, 2]:
        raise click.UsageError('Either "--movie-id" or "--image-id" is required.')

    client = get_client(state)
    try:
        if movie_id is not None:
            keypoint_id = client.extract_keypoint_from_movie(movie_id)
        elif image_id is not None:
            keypoint_id = client.extract_keypoint_from_image(image_id)

        echo(f"Keypoint extraction started. (keypoint id: {color_id(keypoint_id)})")
        if state.use_spinner:
            with yaspin(text="Processing..."):
                response = client.wait_for_extraction(keypoint_id)
        else:
            response = client.wait_for_extraction(keypoint_id)
    except RequestsError as e:
        raise click.ClickException(str(e))

    if response.status == "SUCCESS":
        echo_success("Keypoint extraction is complete.")
    elif response.status == "TIMEOUT":
        echo("Keypoint extraction is timed out.")
    else:
        echo(f"Keypoint extraction failed: {response.failure_detail}")

    if with_drawing:
        echo()
        ctx.invoke(
            draw,
            keypoint_id=keypoint_id,
            out_dir=out_dir,
            rule_str=rule_str,
            rule_file=rule_file,
            no_download=no_download,
        )
