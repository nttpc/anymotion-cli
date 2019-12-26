import click

from encore_api_cli.options import common_options
from encore_api_cli.state import pass_state
from encore_api_cli.utils import get_client


@click.group()
def cli():
    pass


@cli.group()
def analysis():
    """Manege analyses."""
    pass


@analysis.command()
@common_options
@pass_state
def list(state):
    """Show analysis list."""
    c = get_client(state.profile)
    c.show_list('analyses')


@analysis.command()
@click.argument('analysis_id', type=int)
@common_options
@pass_state
def show(state, analysis_id):
    """Display analysis result in JSON format."""
    c = get_client(state.profile)
    result = c.get_analysis(analysis_id)
    click.echo(result)
