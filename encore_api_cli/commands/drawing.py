from typing import Optional

import click

from ..options import common_options
from ..output import echo_json
from ..state import State, pass_state
from ..utils import get_client


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
@click.option(
    "--status",
    type=click.Choice(["SUCCESS", "FAILURE", "PROCESSING", "UNPROCESSED"]),
    help="Get data for the specified status only.",
)
@common_options
@pass_state
def list(state: State, status: Optional[str]) -> None:
    """Show a list of information for all drawn files."""
    client = get_client(state)
    params = None
    if status is not None:
        params = {"execStatus": status}
    # TODO: catch error
    echo_json(client.get_list_data("drawings", params=params))
