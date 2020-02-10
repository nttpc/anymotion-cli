from typing import Optional

import click
from yaspin import yaspin

from ..exceptions import ClickException
from ..options import common_options
from ..output import echo_error, echo_json
from ..sdk import RequestsError
from ..state import State, pass_state
from ..utils import get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.group()
def keypoint() -> None:
    """Show the extracted keypoints."""
    pass


@keypoint.command()
@click.argument("keypoint_id", type=int)
@common_options
@pass_state
def show(state: State, keypoint_id: int) -> None:
    """Show extracted keypoint data."""
    # TODO: add full option or another command
    client = get_client(state)

    try:
        response = client.get_one_data("keypoints", keypoint_id)
    except RequestsError as e:
        raise ClickException(str(e))
    if not isinstance(response, dict):
        raise Exception("response is invalid.")

    status = response.get("execStatus", "FAILURE")
    if status == "SUCCESS":
        data = response.get("keypoint")
        # TODO: remove type: ignore
        if len(data) < state.pager_length:  # type: ignore
            echo_json(data)
        else:
            echo_json(data, pager=True)
    else:
        echo_error("Status is not SUCCESS.")


@keypoint.command()
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
    """Show a list of information for all keypoints."""
    client = get_client(state)

    params = {}
    if status:
        params = {"execStatus": status.upper()}

    try:
        if state.use_spinner:
            with yaspin(text="Retrieving..."):
                data = client.get_list_data("keypoints", params=params)
        else:
            data = client.get_list_data("keypoints", params=params)
    except RequestsError as e:
        raise ClickException(str(e))

    if len(data) < state.pager_length:
        echo_json(data)
    else:
        echo_json(data, pager=True)
