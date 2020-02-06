import click
from yaspin import yaspin

from ..options import common_options
from ..output import echo_json
from ..state import State, pass_state
from ..utils import get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.group()
def image() -> None:
    """Show the information of the uploaded images."""
    pass


@image.command()
@click.argument("image_id", type=int)
@common_options
@pass_state
def show(state: State, image_id: int) -> None:
    """Show image information."""
    client = get_client(state)
    echo_json(client.get_one_data("images", image_id))


@image.command()
@common_options
@pass_state
def list(state: State) -> None:
    """Show a list of information for all images."""
    client = get_client(state)

    # TODO: catch error in get_list_data
    if state.use_spinner:
        with yaspin(text="Retrieving..."):
            data = client.get_list_data("images")
    else:
        data = client.get_list_data("images")

    if len(data) < state.pager_length:
        echo_json(data)
    else:
        echo_json(data, pager=True)
