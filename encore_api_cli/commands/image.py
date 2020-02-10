import click
from click_help_colors import HelpColorsGroup
from yaspin import yaspin

from ..exceptions import ClickException
from ..options import common_options
from ..output import echo_json
from ..sdk import RequestsError
from ..state import State, pass_state
from ..utils import get_client


@click.group(cls=HelpColorsGroup, help_options_color="cyan")
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

    try:
        data = client.get_one_data("images", image_id)
    except RequestsError as e:
        raise ClickException(str(e))

    echo_json(data)


@image.command()
@common_options
@pass_state
def list(state: State) -> None:
    """Show a list of information for all images."""
    client = get_client(state)

    try:
        if state.use_spinner:
            with yaspin(text="Retrieving..."):
                data = client.get_list_data("images")
        else:
            data = client.get_list_data("images")
    except RequestsError as e:
        raise ClickException(str(e))

    if len(data) < state.pager_length:
        echo_json(data)
    else:
        echo_json(data, pager=True)
