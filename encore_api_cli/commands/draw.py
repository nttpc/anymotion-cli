import click

from encore_api_cli.options import common_options
from encore_api_cli.state import pass_state
from encore_api_cli.utils import get_client


def draw_options(f):
    f = click.option(
        "-o",
        "--out_dir",
        default=".",
        type=click.Path(),
        show_default=True,
        help="Path of directory to output drawn file.",
    )(f)
    f = click.option("--no-download", is_flag=True, help="Disable download")(f)
    return f


@click.group()
def cli():
    pass


@cli.command()
@click.argument("keypoint_id", type=int)
@draw_options
@common_options
@pass_state
def draw(state, keypoint_id, out_dir, no_download):
    """Draw keypoints on uploaded movie or image."""
    c = get_client(state)
    url = c.draw_keypoint(keypoint_id)

    # TODO(y_kumiha): すでにファイルが存在する場合
    if url is not None and not no_download:
        c.download(url, out_dir)
