import click

from ..utils import get_client


@click.group()
def cli():
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--profile',
              default='default',
              help='Name of a named profile that you can configure.')
def upload(path, profile):
    """Upload a local movie or image to cloud storage."""
    c = get_client(profile)
    media_id, media_type = c.upload_to_s3(path)
    click.echo(
        f'Uploaded the {media_type} file to '
        f'cloud storage ({media_type}_id: {media_id})'
    )
