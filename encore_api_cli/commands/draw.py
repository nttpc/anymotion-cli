import click

from encore_api_cli.options import common_options
from encore_api_cli.state import pass_state
from encore_api_cli.utils import get_client


@click.group()
def cli():
    pass


@cli.command()
@click.argument('keypoint_id', type=int)
@click.option('-o',
              '--out_dir',
              default='.',
              type=click.Path(),
              show_default=True,
              help='Path of directory to output drawn file.')
@common_options
@pass_state
def draw(state, keypoint_id, out_dir):
    """Draw keypoints on uploaded movie or image."""
    c = get_client(state.profile)
    url = c.draw_keypoint(keypoint_id)

    if url is not None:
        c.download(url, out_dir)
