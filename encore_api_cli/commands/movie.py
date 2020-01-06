import click

from encore_api_cli.options import common_options
from encore_api_cli.output import write_json_data
from encore_api_cli.state import pass_state
from encore_api_cli.utils import get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.group()
def movie():
    """Show the information of the uploaded movies."""
    pass


@movie.command()
@click.argument("movie_id", type=int)
@common_options
@pass_state
def show(state, movie_id):
    """Show movie information."""
    c = get_client(state)
    write_json_data(c.get_info("movies", movie_id), sort_keys=False)


@movie.command()
@common_options
@pass_state
def list(state):
    """Show a list of information for all movies."""
    c = get_client(state)
    write_json_data(c.get_info("movies"), sort_keys=False)
