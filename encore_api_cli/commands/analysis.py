import json

import click

from encore_api_cli.options import common_options
from encore_api_cli.output import echo, echo_json
from encore_api_cli.state import State, pass_state
from encore_api_cli.utils import get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.group()
def analysis() -> None:
    """Show analysis results."""


@analysis.command()
@click.argument("analysis_id", type=int)
@common_options
@pass_state
def show(state: State, analysis_id: int) -> None:
    """Show analysis result."""
    client = get_client(state)
    response = client.get_one_data("analyses", analysis_id)
    if not isinstance(response, dict):
        # TODO: catch error
        raise

    status = response.get("execStatus", "FAILURE")
    if status == "SUCCESS":
        result = response.get("result")
        if not isinstance(result, str):
            # TODO: catch error
            raise
        echo_json(json.loads(result))
    else:
        echo("Status is not SUCCESS.")


@analysis.command()
@common_options
@pass_state
def list(state: State) -> None:
    """Show analysis list."""
    client = get_client(state)
    echo_json(client.get_list_data("analyses"))
