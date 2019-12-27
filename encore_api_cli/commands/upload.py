import click

from encore_api_cli.exceptions import InvalidFileType
from encore_api_cli.exceptions import RequestsError
from encore_api_cli.options import common_options
from encore_api_cli.state import pass_state
from encore_api_cli.utils import get_client


@click.group()
def cli():
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@common_options
@pass_state
def upload(state, path):
    """Upload the local movie or image file to cloud storage."""
    c = get_client(state.profile)

    try:
        media_id, media_type = c.upload_to_s3(path)
    except InvalidFileType as e:
        raise click.BadParameter(e)
    except RequestsError as e:
        raise click.ClickException(e)

    message = (f"{click.style('Success', fg='green')}: "
               f"Uploaded { click.style(path, fg='blue')} "
               'to the cloud storage. '
               f"({click.style(f'{media_type}_id: {media_id}', fg='cyan')})")
    click.echo(message)
