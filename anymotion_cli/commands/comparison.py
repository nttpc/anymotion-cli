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
    short_help="Show the comparison results.",
)
def comparison() -> None:
    """Show the comparison results."""


@comparison.command(short_help="Show the comparison result.")
@click.argument("comparison_id", type=int)
@click.option(
    "--only",
    "--only-difference",
    "only_difference",
    is_flag=True,
    help="Show only difference data.",
)
@click.option("--no-difference", is_flag=True, help="Do not show difference data.")
@click.option("--join", is_flag=True, help="Join the related data.")
@common_options
@pass_state
def show(
    state: State,
    comparison_id: int,
    only_difference: bool,
    no_difference: bool,
    join: bool,
) -> None:
    """Show the comparison result."""
    if only_difference and no_difference:
        raise click.UsageError(
            '"--only, --only-difference" and "--no-difference" options cannot be used '
            "at the same time."
        )

    client = get_client(state)

    try:
        response = client.get_comparison(comparison_id, join_data=join)
    except RequestsError as e:
        raise ClickException(str(e))
    if not isinstance(response, dict):
        raise Exception("Response is invalid.")

    data = response.get("difference") or []
    pager = len(data) >= state.pager_length

    if no_difference:
        response.pop("difference")
        echo_json(response)
    elif only_difference:
        status = response.get("execStatus", "FAILURE")
        if status == "SUCCESS":
            echo_json(data, pager=pager)
        else:
            raise ClickException("Status is not SUCCESS.")
    else:
        echo_json(response, pager=pager)


@comparison.command(short_help="Show a list of information for all comparisons.")
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
    """Show a list of information for all comparisons."""
    client = get_client(state)

    params = {}
    if status:
        params = {"execStatus": status}

    try:
        if state.use_spinner:
            with yaspin(text="Retrieving..."):
                data = client.get_comparisons(params=params)
        else:
            data = client.get_comparisons(params=params)
    except RequestsError as e:
        raise ClickException(str(e))

    if len(data) < state.pager_length:
        echo_json(data)
    else:
        echo_json(data, pager=True)
