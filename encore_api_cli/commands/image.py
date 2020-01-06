import click

from encore_api_cli.options import common_options
from encore_api_cli.output import write_json_data
from encore_api_cli.state import pass_state
from encore_api_cli.utils import get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.group()
def image():
    """Show the information of the uploaded images."""
    pass


@image.command()
@click.argument("image_id", type=int)
@common_options
@pass_state
def show(state, image_id):
    """Show image information."""
    c = get_client(state)
    write_json_data(c.get_info("images", image_id), sort_keys=False)


@image.command()
@common_options
@pass_state
def list(state):
    """Show a list of information for all images."""
    c = get_client(state)
    write_json_data(c.get_info("images"), sort_keys=False)
