from typing import Optional

import click
from anymotion_sdk import RequestsError
from yaspin import yaspin

from ..click_custom import CustomGroup
from ..exceptions import ClickException
from ..options import common_options
from ..output import echo_json
from ..state import State, pass_state
from ..utils import get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.group(
    cls=CustomGroup,
    help_options_color="cyan",
    short_help="Show the information of the drawn images or movies.",
)
def drawing() -> None:
    """Show the information of the drawn images or movies."""


@drawing.command(short_help="Show drawn files information.")
@click.argument("drawing_id", type=int)
@click.option("--join", is_flag=True, help="Join the related data.")
@common_options
@pass_state
def show(state: State, drawing_id: int, join: bool) -> None:
    """Show drawn files information."""
    client = get_client(state)

    try:
        data = client.get_drawing(drawing_id, join_data=join)
    except RequestsError as e:
        raise ClickException(str(e))

    echo_json(data)


@drawing.command(short_help="Show a list of information for all drawn files.")
@click.option(
    "--status",
    type=click.Choice(
        ["SUCCESS", "FAILURE", "PROCESSING", "UNPROCESSED"], case_sensitive=False
    ),
    help="Get data for the specified status only.",
)
@common_options
@pass_state
def list(state: State, status: Optional[str]) -> None:
    """Show a list of information for all drawn files."""
    client = get_client(state)

    params = {}
    if status:
        params = {"execStatus": status}

    try:
        if state.use_spinner:
            with yaspin(text="Retrieving..."):
                data = client.get_drawings(params=params)
        else:
            data = client.get_drawings(params=params)
    except RequestsError as e:
        raise ClickException(str(e))

    if len(data) < state.pager_length:
        echo_json(data)
    else:
        echo_json(data, pager=True)
