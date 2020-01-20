import io
from typing import Optional

import click

from encore_api_cli.commands.analysis import show
from encore_api_cli.options import common_options
from encore_api_cli.output import echo, echo_success
from encore_api_cli.state import State, pass_state
from encore_api_cli.utils import color_id, get_client, parse_rule


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.command()
@click.argument("keypoint_id", type=int)
@click.option("--rule", "rule_str", help="Analysis rules in JSON format.")
@click.option(
    "--rule-file", type=click.File(), help="Analysis rules file in JSON format."
)
@click.option("--show_result", is_flag=True)
@common_options
@pass_state
@click.pass_context
def analyze(
    ctx: click.core.Context,
    state: State,
    keypoint_id: int,
    rule_str: Optional[str],
    rule_file: Optional[io.TextIOWrapper],
    show_result: bool,
) -> None:
    """Analyze the extracted keypoint data."""
    if rule_str is not None and rule_file is not None:
        raise click.UsageError(
            '"rule" and "rule_file" options cannot be used at the same time.'
        )

    rule = None
    if rule_str is not None:
        rule = parse_rule(rule_str)
    elif rule_file is not None:
        rule = parse_rule(rule_file.read())

    client = get_client(state)
    analysis_id = client.analyze_keypoint(keypoint_id, rule=rule)
    echo(f"Analysis started. (analysis_id: {color_id(analysis_id)})")

    status = client.wait_for_analysis(analysis_id)
    if status == "SUCCESS":
        echo_success("Analysis is complete.")
        if show_result:
            ctx.invoke(show, analysis_id=analysis_id)
    elif status == "TIMEOUT":
        echo("Analysis is timed out.")
    else:
        echo("Analysis failed.")
