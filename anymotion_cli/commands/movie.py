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
    short_help="Show the information of the uploaded movies.",
)
def movie() -> None:
    """Show the information of the uploaded movies."""


@movie.command(short_help="Show movie information.")
@click.argument("movie_id", type=int)
@common_options
@pass_state
def show(state: State, movie_id: int) -> None:
    """Show movie information."""
    client = get_client(state)

    try:
        data = client.get_movie(movie_id)
    except RequestsError as e:
        raise ClickException(str(e))

    echo_json(data)


@movie.command(short_help="Show a list of information for all movies.")
@common_options
@pass_state
def list(state: State) -> None:
    """Show a list of information for all movies."""
    client = get_client(state)

    try:
        if state.use_spinner:
            with yaspin(text="Retrieving..."):
                data = client.get_movies()
        else:
            data = client.get_movies()
    except RequestsError as e:
        raise ClickException(str(e))

    if len(data) < state.pager_length:
        echo_json(data)
    else:
        echo_json(data, pager=True)
