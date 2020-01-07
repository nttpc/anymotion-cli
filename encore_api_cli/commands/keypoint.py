import json

import click

from encore_api_cli.commands.draw import draw, draw_options
from encore_api_cli.exceptions import RequestsError
from encore_api_cli.options import common_options
from encore_api_cli.output import write_json_data, write_message, write_success
from encore_api_cli.state import pass_state
from encore_api_cli.utils import color_id, get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.group()
def keypoint():
    """Extract keypoints and show the list."""
    pass


@keypoint.command()
@click.argument("keypoint_id", type=int)
@common_options
@pass_state
def show(state, keypoint_id):
    """Show extracted keypoint data."""
    c = get_client(state)
    response = c.get_info("keypoints", keypoint_id)
    status = response.get("exec_status", "FAILURE")
    if status == "SUCCESS":
        keypoint = response.get("keypoint")
        write_json_data(json.loads(keypoint), sort_keys=False)
    else:
        write_message("Status is not SUCCESS.")


@keypoint.command()
@common_options
@pass_state
def list(state):
    """Show a list of information for all keypoints."""
    c = get_client(state)
    write_json_data(c.get_info("keypoints"), sort_keys=False)


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
def extract(ctx, state, movie_id, image_id, with_drawing, out_dir, no_download):
    """Extract keypoints from uploaded images or movies."""
    if [movie_id, image_id].count(None) in [0, 2]:
        raise click.UsageError('Either "movie_id" or "image_id" is required.')

    c = get_client(state)
    try:
        if movie_id is not None:
            keypoint_id = c.extract_keypoint_from_movie(movie_id)
        else:
            keypoint_id = c.extract_keypoint_from_image(image_id)

        write_message(
            f"Keypoint extraction started. (keypoint_id: {color_id(keypoint_id)})"
        )
        status = c.wait_for_extraction(keypoint_id)
    except RequestsError as e:
        raise click.ClickException(e)

    if status == "SUCCESS":
        write_success("Keypoint extraction is complete.")
    elif status == "TIMEOUT":
        write_message("Keypoint extraction is timed out.")
    else:
        write_message("Keypoint extraction failed.")

    if with_drawing:
        write_message()
        ctx.invoke(
            draw, keypoint_id=keypoint_id, out_dir=out_dir, no_download=no_download
        )
