import click

from encore_api_cli.utils import get_client


@click.group()
def cli():
    pass


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
