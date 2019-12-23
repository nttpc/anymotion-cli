import click

from encore_api_cli.utils import get_client


@click.group()
def cli():
    pass


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
