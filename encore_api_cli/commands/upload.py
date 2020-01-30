import click

from encore_api_cli.sdk.exceptions import InvalidFileType, RequestsError
from encore_api_cli.options import common_options
from encore_api_cli.output import echo_success
from encore_api_cli.state import State, pass_state
from encore_api_cli.utils import color_id, color_path, get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@common_options
@pass_state
def upload(state: State, path: str) -> None:
    """Upload the local movie or image file to the cloud storage."""
    client = get_client(state)

    try:
        media_id, media_type = client.upload_to_s3(path)
    except InvalidFileType as e:
        raise click.BadParameter(str(e))
    except RequestsError as e:
        raise click.ClickException(str(e))

    cpath = color_path(path)
    cid = color_id(media_id)
    echo_success(f"Uploaded {cpath} to the cloud storage. ({media_type}_id: {cid})")
