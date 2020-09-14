import click
from anymotion_sdk import FileTypeError, RequestsError

from ..click_custom import CustomCommand
from ..exceptions import ClickException
from ..options import common_options
from ..output import echo_success
from ..state import State, pass_state
from ..utils import color_id, color_path, get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.command(
    cls=CustomCommand,
    help_options_color="cyan",
    short_help="Upload the local movie or image file to the cloud storage.",
)
@click.argument("path", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--text",
    default="Created by AnyMotion CLI.",
    help="Description of the upload file.",
)
@common_options
@pass_state
def upload(state: State, path: str, text: str) -> None:
    """Upload the local movie or image file to the cloud storage."""
    client = get_client(state)

    try:
        result = client.upload(path, text=text)
    except FileTypeError as e:
        raise click.BadParameter(str(e))
    except RequestsError as e:
        raise ClickException(str(e))

    cpath = color_path(path)

    if result.image_id:
        cid = color_id(result.image_id)
        media_type = "image"
    else:
        cid = color_id(result.movie_id)
        media_type = "movie"
    echo_success(f"Uploaded {cpath} to the cloud storage. ({media_type} id: {cid})")

    return result
