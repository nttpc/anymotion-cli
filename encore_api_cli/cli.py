import click

from . import __version__
from .client import Client
from .config import Config


@click.group()
@click.version_option(version=__version__)
def cli():
    """Command Line Interface for AnyMotion API."""
    pass


@cli.group(invoke_without_command=True)
@click.option('--profile',
              default='default',
              help='Name of a named profile that you can configure.')
@click.pass_context
def configure(ctx, profile):
    """Configure your AnyMotion Access Token."""
    if ctx.invoked_subcommand is None:
        config = Config(profile)
        config.url = click.prompt('AnyMotion API URL', default=config.url)
        config.token = click.prompt('AnyMotion Access Token', default=config.token)
        config.update()


@configure.command()
def list():
    """Show the configuration you set."""
    config = Config()
    config.show()


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
        f'Uploaded the {media_type} file to cloud storage ({media_type}_id: {media_id})'
    )


@cli.group()
def movie():
    """Manege movies."""
    pass


@movie.command()
@click.option('--profile',
              default='default',
              help='Name of a named profile that you can configure.')
def list(profile):
    """Show movie list."""
    c = get_client(profile)
    c.show_list('movies')


@cli.group()
def image():
    """Manege images."""
    pass


@image.command()
@click.option('--profile',
              default='default',
              help='Name of a named profile that you can configure.')
def list(profile):
    """Show image list."""
    c = get_client(profile)
    c.show_list('images')


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
@click.option('--profile',
              default='default',
              help='Name of a named profile that you can configure.')
def extract(profile, movie_id, image_id):
    """Extract keypoints from uploaded images or movies."""
    if movie_id is None and image_id is None:
        raise click.UsageError('Either "movie_id" or "image_id" is required.')

    c = get_client(profile)
    c.extract_keypoint(movie_id=movie_id, image_id=image_id)


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
@click.option('--profile',
              default='default',
              help='Name of a named profile that you can configure.')
def draw(profile, keypoint_id, rule_id, out_dir):
    """Draw keypoints on uploaded movie or image."""
    c = get_client(profile)
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
@click.option('--profile',
              default='default',
              help='Name of a named profile that you can configure.')
def analyze(profile, keypoint_id, rule_id, show_result):
    """Analyze keypoints data and get information such as angles."""
    c = get_client(profile)
    result = c.analyze_keypoint(keypoint_id, rule_id)
    if show_result:
        click.echo(result)


@cli.group()
def analysis():
    """Manege analyses."""
    pass


@analysis.command()
@click.option('--profile',
              default='default',
              help='Name of a named profile that you can configure.')
def list(profile):
    """Show analysis list."""
    c = get_client(profile)
    c.show_list('analyses')


@analysis.command()
@click.argument('analysis_id', type=int)
@click.option('--profile',
              default='default',
              help='Name of a named profile that you can configure.')
def show(profile, analysis_id):
    """Display analysis result in JSON format."""
    c = get_client(profile)
    result = c.get_analysis(analysis_id)
    click.echo(result)


def get_client(profile):
    config = Config(profile)
    if not config.is_ok:
        message = ' '.join([
            'The access token is invalid or not set.',
            'Run "encore configure" to set token.'
        ])
        raise click.ClickException(message)
    return Client(config.token, config.url)


def main():
    cli()


if __name__ == "__main__":
    main()
