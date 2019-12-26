import click

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
    """Upload a local movie or image to cloud storage."""
    c = get_client(state.profile)
    media_id, media_type = c.upload_to_s3(path)
    click.echo(
        f'Uploaded the {media_type} file to '
        f'cloud storage ({media_type}_id: {media_id})'
    )
