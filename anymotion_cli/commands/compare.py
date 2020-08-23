import click
from anymotion_sdk import RequestsError
from click_help_colors import HelpColorsGroup
from yaspin import yaspin

from ..exceptions import ClickException
from ..options import common_options
from ..output import echo, echo_success
from ..state import State, pass_state
from ..utils import color_id, get_client
from .draw import draw


@click.group(cls=HelpColorsGroup, help_options_color="cyan")
def cli() -> None:  # noqa: D103
    pass


@cli.command(short_help="Compare the two extracted keypoint data.")
@click.argument("source_id", type=int)
@click.argument("target_id", type=int)
@click.option(
    "-d", "--with-drawing", is_flag=True, help="Drawing with comparison results.",
)
@common_options
@pass_state
@click.pass_context
def compare(
    ctx: click.Context,
    state: State,
    source_id: int,
    target_id: int,
    with_drawing: bool,
) -> None:
    """Compare the two extracted keypoint data.

    SOURCE_ID and TARGET_ID are extracted keypoint ids.
    """
    client = get_client(state)

    try:
        comparison_id = client.compare_keypoint(source_id, target_id)
        echo(f"Comparison started. (comparison id: {color_id(comparison_id)})")

        if state.use_spinner:
            with yaspin(text="Processing..."):
                response = client.wait_for_comparison(comparison_id)
        else:
            response = client.wait_for_comparison(comparison_id)
    except RequestsError as e:
        raise ClickException(str(e))

    if response.status == "SUCCESS":
        echo_success("Comparison is complete.")
    elif response.status == "TIMEOUT":
        raise ClickException("Comparison is timed out.")
    else:
        raise ClickException(f"Comparison failed.\n{response.failure_detail}")

    if with_drawing:
        echo()
        ctx.invoke(draw, comparison_id=comparison_id)
