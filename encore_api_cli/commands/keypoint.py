import click

from encore_api_cli.utils import get_client


@click.group()
def cli():
    pass


@cli.group()
def keypoint():
    """Extract keypoints and show the list."""
    pass


@keypoint.command()
@click.option('--profile',
              default='default',
              help='Name of a named profile that you can configure.')
def list(profile):
    """Show keypoint list."""
    c = get_client(profile)
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
@click.option('-d',
              '--with_drawing',
              is_flag=True,
              help='Flag for whether to draw at the same time.')
@click.option('-o',
              '--out_dir',
              default='.',
              type=click.Path(),
              show_default=True,
              help='Path of directory to output drawn file.')
@click.option('--profile',
              default='default',
              help='Name of a named profile that you can configure.')
def extract(profile, movie_id, image_id, with_drawing, out_dir):
    """Extract keypoints from uploaded images or movies."""
    if movie_id is None and image_id is None:
        raise click.UsageError('Either "movie_id" or "image_id" is required.')

    c = get_client(profile)
    keypoint_id = c.extract_keypoint(movie_id=movie_id, image_id=image_id)

    if with_drawing:
        url = c.draw_keypoint(keypoint_id)
        if url is not None:
            c.download(url, out_dir)


@keypoint.command()
@click.argument('keypoint_id', type=int)
@click.option('--profile',
              default='default',
              help='Name of a named profile that you can configure.')
def show(profile, keypoint_id):
    """Display extracted keypoint data in JSON format."""
    c = get_client(profile)
    keypoint = c.get_keypoint(keypoint_id)
    click.echo(keypoint)
