import click

from . import __version__
from .client import Client


@click.group()
@click.option('--token',
              required=True,
              envvar='API_TOKEN',
              help='Access token for authorization.')
@click.option('--url',
              'base_url',
              default='https://dev.api.anymotion.jp/api/v1/',
              envvar='API_URL',
              show_default=True,
              help='URL of AnyMotion API.')
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, token, base_url, version):
    """Command Line Interface for AnyMotion API."""
    ctx.ensure_object(dict)
    ctx.obj['client'] = Client(token, base_url)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.pass_context
def upload(ctx, path):
    """Upload a local movie or image to cloud storage."""
    c = ctx.obj['client']
    media_id, media_type = c.upload_to_s3(path)
    click.echo(
        f'uploaded the {media_type} file to cloud storage ({media_type}_id: {media_id})'
    )


@cli.group()
def movie():
    """Manege movies."""
    pass


@movie.command()
@click.pass_context
def list(ctx):
    """Show movie list."""
    c = ctx.obj['client']
    c.show_list('movies')


@cli.group()
def image():
    """Manege images."""
    pass


@image.command()
@click.pass_context
def list(ctx):
    """Show image list."""
    c = ctx.obj['client']
    c.show_list('images')


@cli.group()
def keypoint():
    """Extract keypoints and show the list."""
    pass


@keypoint.command()
@click.pass_context
def list(ctx):
    """Show keypoint list."""
    c = ctx.obj['client']
    c.show_list('keypoints')


@keypoint.command()
@click.option(
    '--movie_id',
    type=int,
    help='ID of movie to extrat, either movie_id or image_id is required.')
@click.option(
    '--image_id',
    type=int,
    help='ID of image to extrat, either movie_id or image_id is required.')
@click.pass_context
def extract(ctx, movie_id, image_id):
    """Extract keypoints from uploaded images or movies."""
    if movie_id is None and image_id is None:
        raise click.UsageError('Either "movie_id" or "image_id" is required.')

    c = ctx.obj['client']
    c.extract_keypoint(movie_id=movie_id, image_id=image_id)


@keypoint.command()
@click.argument('keypoint_id', type=int)
@click.pass_context
def show(ctx, keypoint_id):
    """Display extracted keypoint data in JSON format."""
    c = ctx.obj['client']
    keypoint = c.get_keypoint(keypoint_id)
    click.echo(keypoint)


@cli.command()
@click.argument('keypoint_id', type=int)
@click.option('--rule_id',
              default=0,
              type=int,
              show_default=True,
              help='Rule ID that defines how to draw.')
@click.option('-o',
              '--out_dir',
              default='.',
              type=click.Path(),
              show_default=True,
              help='Path of directory to output drawn file.')
@click.pass_context
def drawing(ctx, keypoint_id, rule_id, out_dir):
    """Draw keypoints on uploaded movie or image."""
    c = ctx.obj['client']
    url = c.draw_keypoint(keypoint_id, rule_id)

    if url is not None:
        c.download(url, out_dir)


@cli.command()
@click.argument('keypoint_id', type=int)
@click.option('--rule_id',
              required=True,
              type=int,
              help='Rule ID that defines how to analyze.')
@click.option('--show_result', is_flag=True)
@click.pass_context
def analysis(ctx, keypoint_id, rule_id, show_result):
    """Analyze keypoints data and get information such as angles."""
    c = ctx.obj['client']
    result = c.analyze_keypoint(keypoint_id, rule_id)
    if show_result:
        click.echo(result)


def main():
    cli()


if __name__ == "__main__":
    main()
