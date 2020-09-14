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
    short_help="Show the information of the uploaded images.",
)
def image() -> None:
    """Show the information of the uploaded images."""


@image.command(short_help="Show image information.")
@click.argument("image_id", type=int)
@common_options
@pass_state
def show(state: State, image_id: int) -> None:
    """Show image information."""
    client = get_client(state)

    try:
        data = client.get_image(image_id)
    except RequestsError as e:
        raise ClickException(str(e))

    echo_json(data)


@image.command(short_help="Show a list of information for all images.")
@common_options
@pass_state
def list(state: State) -> None:
    """Show a list of information for all images."""
    client = get_client(state)

    try:
        if state.use_spinner:
            with yaspin(text="Retrieving..."):
                data = client.get_images()
        else:
            data = client.get_images()
    except RequestsError as e:
        raise ClickException(str(e))

    if len(data) < state.pager_length:
        echo_json(data)
    else:
        echo_json(data, pager=True)
