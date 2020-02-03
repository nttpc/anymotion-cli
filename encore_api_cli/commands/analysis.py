from typing import Optional

import click

from ..options import common_options
from ..output import echo, echo_json
from ..state import State, pass_state
from ..utils import get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.group()
def analysis() -> None:
    """Show the analysis results."""


@analysis.command()
@click.argument("analysis_id", type=int)
@common_options
@pass_state
def show(state: State, analysis_id: int) -> None:
    """Show the analysis result."""
    client = get_client(state)
    response = client.get_one_data("analyses", analysis_id)
    if not isinstance(response, dict):
        # TODO: catch error
        raise

    status = response.get("execStatus", "FAILURE")
    if status == "SUCCESS":
        echo_json(response.get("result"))
    else:
        echo("Status is not SUCCESS.")


@analysis.command()
@click.option(
    "--status",
    type=click.Choice(["SUCCESS", "FAILURE", "PROCESSING", "UNPROCESSED"]),
    help="Get data for the specified status only.",
)
@common_options
@pass_state
def list(state: State, status: Optional[str]) -> None:
    """Show the analysis list."""
    client = get_client(state)
    params = None
    if status is not None:
        params = {"execStatus": status}
    # TODO: catch error
    echo_json(client.get_list_data("analyses", params=params))
