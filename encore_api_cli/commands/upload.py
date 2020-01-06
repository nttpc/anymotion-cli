import click

from encore_api_cli.exceptions import InvalidFileType, RequestsError
from encore_api_cli.options import common_options
from encore_api_cli.output import write_success
from encore_api_cli.state import State, pass_state
from encore_api_cli.utils import get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@common_options
@pass_state
def upload(state: State, path: str) -> None:
    """Upload the local movie or image file to the cloud storage."""
    c = get_client(state)

    try:
        media_id, media_type = c.upload_to_s3(path)
    except InvalidFileType as e:
        raise click.BadParameter(str(e))
    except RequestsError as e:
        raise click.ClickException(str(e))

    write_success(
        "Uploaded {path} to the cloud storage. ({media_type}_id: {media_id})".format(
            path=click.style(path, fg="blue"),
            media_type=media_type,
            media_id={click.style(str(media_id), fg="cyan")},
        )
    )
