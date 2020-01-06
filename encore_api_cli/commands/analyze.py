import click

from encore_api_cli.options import common_options
from encore_api_cli.state import pass_state
from encore_api_cli.utils import get_client


@click.group()
def cli():
    pass


@cli.command()
@click.argument("keypoint_id", type=int)
@click.option("--show_result", is_flag=True)
@common_options
@pass_state
def analyze(state, keypoint_id, show_result):
    """Analyze keypoints data and get information such as angles."""
    c = get_client(state)
    result = c.analyze_keypoint(keypoint_id)
    if show_result:
        click.echo(result)
