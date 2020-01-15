import click

from encore_api_cli.options import common_options
from encore_api_cli.output import echo_json
from encore_api_cli.state import State, pass_state
from encore_api_cli.utils import get_client


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
    c = get_client(state)
    echo_json(c.get_info("images", image_id), sort_keys=False)


@image.command()
@common_options
@pass_state
def list(state: State) -> None:
    """Show a list of information for all images."""
    c = get_client(state)
    echo_json(c.get_info("images"), sort_keys=False)
