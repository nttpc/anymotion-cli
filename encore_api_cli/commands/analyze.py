import click

from encore_api_cli.options import common_options
from encore_api_cli.output import write_message, write_success
from encore_api_cli.state import pass_state
from encore_api_cli.utils import color_id, get_client
from encore_api_cli.commands.analysis import show


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.command()
@click.argument("keypoint_id", type=int)
@click.option("--show_result", is_flag=True)
@common_options
@pass_state
@click.pass_context
def analyze(ctx, state, keypoint_id, show_result):
    """Analyze the extracted keypoint data."""
    c = get_client(state)
    analysis_id = c.analyze_keypoint(keypoint_id)
    write_message(f"Start the analysis. (analysis_id: {color_id(analysis_id)})")

    status = c.wait_for_analysis(analysis_id)
    if status == "SUCCESS":
        write_success("Analysis is complete.")
        if show_result:
            ctx.invoke(show, analysis_id=analysis_id)
    elif status == "TIMEOUT":
        write_message("Analysis is timed out.")
    else:
        write_message("Analysis failed.")
