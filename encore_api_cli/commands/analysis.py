from typing import Optional

import click
from click_help_colors import HelpColorsGroup
from yaspin import yaspin

from ..exceptions import ClickException
from ..options import common_options
from ..output import echo_error, echo_json
from ..sdk import RequestsError
from ..state import State, pass_state
from ..utils import get_client


@click.group(cls=HelpColorsGroup, help_options_color="cyan")
def cli() -> None:  # noqa: D103
    pass


@cli.group(short_help='Show the analysis results.')
def analysis() -> None:
    """Show the analysis results."""


@analysis.command(short_help="Show the analysis result.")
@click.argument("analysis_id", type=int)
@common_options
@pass_state
def show(state: State, analysis_id: int) -> None:
    """Show the analysis result."""
    client = get_client(state)

    try:
        response = client.get_one_data("analyses", analysis_id)
    except RequestsError as e:
        raise ClickException(str(e))
    if not isinstance(response, dict):
        raise Exception("response is invalid.")

    status = response.get("execStatus", "FAILURE")
    if status == "SUCCESS":
        echo_json(response.get("result"))
    else:
        echo_error("Status is not SUCCESS.")


@analysis.command(short_help="Show the analysis list.")
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
    """Show the analysis list."""
    client = get_client(state)

    params = {}
    if status:
        params = {"execStatus": status.upper()}

    try:
        if state.use_spinner:
            with yaspin(text="Retrieving..."):
                data = client.get_list_data("analyses", params=params)
        else:
            data = client.get_list_data("analyses", params=params)
    except RequestsError as e:
        raise ClickException(str(e))

    if len(data) < state.pager_length:
        echo_json(data)
    else:
        echo_json(data, pager=True)
