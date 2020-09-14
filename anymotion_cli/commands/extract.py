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
from ..utils import color_id, echo_invalid_option_warning, get_client
from .download import check_download_options, download_options
from .draw import check_draw_options, draw, draw_options
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
    metavar="PATH",
    help="Path of the movie or image file to extract.",
)
@click.option(
    "-d",
    "--with-drawing",
    is_flag=True,
    help="Drawing with the extracted keypoints.",
)
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
    path: Optional[Path],
    with_drawing: bool,
    **kwargs,
) -> None:
    """Extract keypoints from image or movie.

    Either '--image-id' or '--movie-id' or '--path' is required.

    When using the '--with-drawing' option, you can use drawing options such as
    '--rule', '--bg-rule', and '--rule-file', and '--download / --no-download'.
    In addition, when downloading the drawn file, you can use download options
    such as '-o, --out', '--force' and '--open / --no-open'.
    """
    required_options = [image_id, movie_id, path]
    if required_options.count(None) != len(required_options) - 1:
        raise click.UsageError(
            "Either '--image-id' or '--movie-id' or '--path' is required"
        )
    if not with_drawing:
        args = click.get_os_args()
        options = check_draw_options(args) + check_download_options(args)
        echo_invalid_option_warning("using '--with-drawing'", options)

    client = get_client(state)

    result = None
    if path is not None:
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
