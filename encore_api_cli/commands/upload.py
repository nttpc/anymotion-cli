import click
from click_help_colors import HelpColorsGroup

from ..exceptions import ClickException
from ..options import common_options
from ..output import echo_success
from ..sdk import FileTypeError, RequestsError
from ..state import State, pass_state
from ..utils import color_id, color_path, get_client


@click.group(cls=HelpColorsGroup, help_options_color="cyan")
def cli() -> None:  # noqa: D103
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True, dir_okay=False))
@common_options
@pass_state
def upload(state: State, path: str) -> None:
    """Upload the local movie or image file to the cloud storage."""
    client = get_client(state)

    try:
        media_id, media_type = client.upload_to_s3(path)
    except FileTypeError as e:
        raise click.BadParameter(str(e))
    except RequestsError as e:
        raise ClickException(str(e))

    cpath = color_path(path)
    cid = color_id(media_id)
    echo_success(f"Uploaded {cpath} to the cloud storage. ({media_type} id: {cid})")
