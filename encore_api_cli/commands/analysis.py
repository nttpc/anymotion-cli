import click

from ..utils import get_client


@click.group()
def cli():
    pass


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
