import click

from encore_api_cli.commands.draw import draw
from encore_api_cli.exceptions import RequestsError
from encore_api_cli.options import common_options
from encore_api_cli.state import pass_state
from encore_api_cli.utils import get_client


@click.group()
def cli():
    pass


@cli.group()
def keypoint():
    """Extract keypoints and show the list."""
    pass


@keypoint.command()
@common_options
@pass_state
def list(state):
    """Show keypoint list."""
    c = get_client(state.profile)
    c.show_list("keypoints")


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
@click.option(
    "-o",
    "--out_dir",
    default=".",
    type=click.Path(),
    show_default=True,
    help="Path of directory to output drawn file.",
)
@common_options
@pass_state
@click.pass_context
def extract(ctx, state, movie_id, image_id, with_drawing, out_dir):
    """Extract keypoints from uploaded images or movies."""
    if [movie_id, image_id].count(None) in [0, 2]:
        raise click.UsageError('Either "movie_id" or "image_id" is required.')

    c = get_client(state.profile)
    try:
        if movie_id is not None:
            keypoint_id = c.extract_keypoint_from_movie(movie_id)
        else:
            keypoint_id = c.extract_keypoint_from_image(image_id)

        click.echo(f"Keypoint extraction started. (keypoint_id: {keypoint_id})")
        status = c.wait_for_extraction(keypoint_id)
    except RequestsError as e:
        raise click.ClickException(e)

    if status == "SUCCESS":
        click.echo("Keypoint extraction is complete.")
    elif status == "TIMEOUT":
        click.echo("Keypoint extraction is timed out.")
    else:
        click.echo("Keypoint extraction failed.")

    if with_drawing:
        ctx.invoke(draw, keypoint_id=keypoint_id, out_dir=out_dir)


@keypoint.command()
@click.argument("keypoint_id", type=int)
@common_options
@pass_state
def show(state, keypoint_id):
    """Display extracted keypoint data in JSON format."""
    c = get_client(state.profile)
    keypoint = c.get_keypoint(keypoint_id)
    click.echo(keypoint)
