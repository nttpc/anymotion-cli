from typing import Optional

import click
from anymotion_sdk import RequestsError
from yaspin import yaspin

from ..click_custom import CustomGroup
from ..exceptions import ClickException
from ..options import common_options
from ..output import echo_json, echo_warning
from ..state import State, pass_state
from ..utils import get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.group(
    cls=CustomGroup, help_options_color="cyan", short_help="Show the analysis results."
)
def analysis() -> None:
    """Show the analysis results."""


@analysis.command(short_help="Show the analysis result.")
@click.argument("analysis_id", type=int)
@click.option(
    "--only",
    "--only-result",
    "only_result",
    is_flag=True,
    help="Show only result data.",
)
@click.option("--no-result", is_flag=True, help="Do not show result data.")
@click.option("--join", is_flag=True, help="Join the related data.")
@common_options
@pass_state
def show(
    state: State, analysis_id: int, only_result: bool, no_result: bool, join: bool
) -> None:
    """Show the analysis result."""
    if only_result and no_result:
        raise click.UsageError(
            '"--only, --only-result" and "--no-result" options cannot be used '
            "at the same time."
        )

    client = get_client(state)

    try:
        response = client.get_analysis(analysis_id, join_data=join)
    except RequestsError as e:
        raise ClickException(str(e))
    if not isinstance(response, dict):
        raise Exception("Response is invalid.")

    data = response.get("result") or []
    try:
        count = sum([len(row["values"]) for row in data])
    except Exception as e:
        echo_warning(f"Response is invalid: {e}")
        count = 0
    pager = count >= state.pager_length

    if no_result:
        response.pop("result")
        echo_json(response)
    elif only_result:
        status = response.get("execStatus", "FAILURE")
        if status == "SUCCESS":
            echo_json(data, pager=pager)
        else:
            raise ClickException("Status is not SUCCESS.")
    else:
        echo_json(response, pager=pager)


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
        params = {"execStatus": status}

    try:
        if state.use_spinner:
            with yaspin(text="Retrieving..."):
                data = client.get_analyses(params=params)
        else:
            data = client.get_analyses(params=params)
    except RequestsError as e:
        raise ClickException(str(e))

    if len(data) < state.pager_length:
        echo_json(data)
    else:
        echo_json(data, pager=True)
