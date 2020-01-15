from typing import Optional

import click

from encore_api_cli.commands.analysis import show
from encore_api_cli.options import common_options
from encore_api_cli.output import write_message, write_success
from encore_api_cli.state import State, pass_state
from encore_api_cli.utils import color_id, get_client, parse_rule


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.command()
@click.argument("keypoint_id", type=int)
@click.option("--rule", help="Analysis rules in JSON format.")
@click.option("--show_result", is_flag=True)
@common_options
@pass_state
@click.pass_context
def analyze(
    ctx: click.core.Context,
    state: State,
    keypoint_id: int,
    rule: Optional[str],
    show_result: bool,
) -> None:
    """Analyze the extracted keypoint data."""
    c = get_client(state)
    analysis_id = c.analyze_keypoint(keypoint_id, rule=parse_rule(rule))
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
