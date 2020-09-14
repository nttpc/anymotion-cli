import click
from anymotion_sdk import RequestsError
from yaspin import yaspin

from ..click_custom import CustomCommand
from ..exceptions import ClickException
from ..options import common_options
from ..output import echo, echo_success
from ..state import State, pass_state
from ..utils import color_id, echo_invalid_option_warning, get_client
from .download import check_download_options, download_options
from .draw import check_draw_options, draw, draw_options


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.command(
    cls=CustomCommand,
    help_options_color="cyan",
    short_help="Compare the two extracted keypoint data.",
)
@click.argument("source_id", type=int)
@click.argument("target_id", type=int)
@click.option(
    "-d",
    "--with-drawing",
    is_flag=True,
    help="Drawing with comparison results.",
)
@draw_options
@download_options
@common_options
@pass_state
@click.pass_context
def compare(
    ctx: click.Context,
    state: State,
    source_id: int,
    target_id: int,
    with_drawing: bool,
    **kwargs,
) -> None:
    """Compare the two extracted keypoint data.

    SOURCE_ID and TARGET_ID are extracted keypoint ids.

    When using the '--with-drawing' option, you can use drawing options such as
    '--rule', '--bg-rule', and '--rule-file', and '--download / --no-download'.
    In addition, when downloading the drawn file, you can use download options
    such as '-o, --out', '--force' and '--open / --no-open'.
    """
    if not with_drawing:
        args = click.get_os_args()
        options = check_draw_options(args) + check_download_options(args)
        echo_invalid_option_warning("using '--with-drawing'", options)

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
        ctx.invoke(draw, comparison_id=comparison_id, **kwargs)
