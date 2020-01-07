import json

import click

from encore_api_cli.options import common_options
from encore_api_cli.output import write_json_data, write_message
from encore_api_cli.state import pass_state
from encore_api_cli.utils import get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.group()
def analysis():
    """Show analysis results."""


@analysis.command()
@click.argument("analysis_id", type=int)
@common_options
@pass_state
def show(state, analysis_id):
    """Show analysis result."""
    c = get_client(state)
    response = c.get_info("analyses", analysis_id)
    status = response.get("exec_status", "FAILURE")
    if status == "SUCCESS":
        result = response.get("result")
        write_json_data(json.loads(result), sort_keys=False)
    else:
        write_message("Status is not SUCCESS.")


@analysis.command()
@common_options
@pass_state
def list(state):
    """Show analysis list."""
    c = get_client(state)
    write_json_data(c.get_info("analyses"), sort_keys=False)
