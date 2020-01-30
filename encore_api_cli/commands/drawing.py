import click

from encore_api_cli.options import common_options
from encore_api_cli.output import echo_json
from encore_api_cli.state import State, pass_state
from encore_api_cli.utils import get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.group()
def drawing() -> None:
    """Show the information of the drawn images or movies."""
    pass


@drawing.command()
@click.argument("drawing_id", type=int)
@common_options
@pass_state
def show(state: State, drawing_id: int) -> None:
    """Show drawn files information."""
    client = get_client(state)
    echo_json(client.get_one_data("drawings", drawing_id))


@drawing.command()
@common_options
@pass_state
def list(state: State) -> None:
    """Show a list of information for all drawn files."""
    client = get_client(state)
    echo_json(client.get_list_data("drawings"))
