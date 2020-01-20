import io
import json
from typing import Optional

import click

from encore_api_cli.commands.draw import draw, draw_options
from encore_api_cli.exceptions import RequestsError
from encore_api_cli.options import common_options
from encore_api_cli.output import echo, echo_json, echo_success
from encore_api_cli.state import State, pass_state
from encore_api_cli.utils import color_id, get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.group()
def keypoint() -> None:
    """Extract keypoints and show the list."""
    pass


@keypoint.command()
@click.argument("keypoint_id", type=int)
@common_options
@pass_state
def show(state: State, keypoint_id: int) -> None:
    """Show extracted keypoint data."""
    c = get_client(state)
    response = c.get_info("keypoints", keypoint_id)
    if not isinstance(response, dict):
        # TODO: catch error
        raise

    status = response.get("execStatus", "FAILURE")
    if status == "SUCCESS":
        keypoint = response.get("keypoint")
        if not isinstance(keypoint, str):
            # TODO: catch error
            raise
        echo_json(json.loads(keypoint), sort_keys=False)
    else:
        echo("Status is not SUCCESS.")


@keypoint.command()
@common_options
@pass_state
def list(state: State) -> None:
    """Show a list of information for all keypoints."""
    c = get_client(state)
    echo_json(c.get_info("keypoints"), sort_keys=False)


@keypoint.command()
@click.option(
    "--movie_id",
    type=int,
    help="ID of movie to extrat, either movie_id or image_id is required.",
)
@click.option(
    "--image_id",
    type=int,
    help="ID of image to extrat, either movie_id or image_id is required.",
)
@click.option(
    "-d",
    "--with_drawing",
    is_flag=True,
    help="Flag for whether to draw at the same time.",
)
@draw_options
@common_options
@pass_state
@click.pass_context
def extract(
    ctx: click.core.Context,
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
        raise click.UsageError('Either "movie_id" or "image_id" is required.')

    c = get_client(state)
    try:
        if movie_id is not None:
            keypoint_id = c.extract_keypoint_from_movie(movie_id)
        elif image_id is not None:
            keypoint_id = c.extract_keypoint_from_image(image_id)

        echo(f"Keypoint extraction started. (keypoint_id: {color_id(keypoint_id)})")
        status = c.wait_for_extraction(keypoint_id)
    except RequestsError as e:
        raise click.ClickException(str(e))

    if status == "SUCCESS":
        echo_success("Keypoint extraction is complete.")
    elif status == "TIMEOUT":
        echo("Keypoint extraction is timed out.")
    else:
        echo("Keypoint extraction failed.")

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
