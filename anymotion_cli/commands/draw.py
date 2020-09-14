import io
from textwrap import dedent
from typing import Callable, List, Optional, Tuple, Union

import click
from anymotion_sdk import RequestsError
from yaspin import yaspin

from ..click_custom import CustomCommand
from ..exceptions import ClickException
from ..options import common_options
from ..output import echo, echo_success
from ..state import State, pass_state
from ..utils import color_id, echo_invalid_option_warning, get_client, parse_rule
from .download import check_download_options, download, download_options


def draw_options(f: Callable) -> Callable:
    """Set draw options."""
    f = click.option(
        "--download/--no-download",
        "is_download",
        default=None,
        help=(
            "Whether to download the drawn file. "
            'If you change the default value, run "configure set is_download".'
        ),
    )(f)
    f = click.option(
        "--rule-file",
        type=click.File(),
        metavar="PATH",
        help=(
            "Path of the JSON file containing the rules and/or background rule "
            "for the drawing. "
            "It cannot be used with --rule or --bg-rule at the same time."
        ),
    )(f)
    f = click.option(
        "--bg-rule",
        "bg_rule_str",
        help="The background rule written in JSON format for the drawing.",
    )(f)
    f = click.option(
        "--rule", "rule_str", help="The rules written in JSON format for the drawing."
    )(f)
    return f


def check_draw_options(args: List[str]) -> List[str]:
    """Check to see if draw options are being used.

    Returns:
        A list of using option names.
    """
    used_options = set(args) & set(
        ["--rule", "--bg-rule", "--rule-file", "--download", "--no-download"]
    )
    return list(used_options)


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.command(
    cls=CustomCommand,
    help_options_color="cyan",
    short_help="Draw based on the extracted keypoints or comparison results.",
)
@click.option("--keypoint-id", type=int)
@click.option("--comparison-id", type=int)
@draw_options
@download_options
@common_options
@pass_state
@click.pass_context
def draw(
    ctx: click.Context,
    state: State,
    keypoint_id: Optional[int],
    comparison_id: Optional[int],
    rule_str: Optional[str],
    rule_file: Optional[io.TextIOWrapper],
    bg_rule_str: Optional[str],
    is_download: Optional[bool],
    **kwargs,
) -> None:
    """Draw points and/or lines based on the extracted keypoints or comparison results.

    Either "--keypoint-id" or "--comparison-id" is required.

    See below for the format of the rule that can be specified with
    "--rule", "--bg-rule", and "--rule-file":
    https://docs.anymotion.jp/drawing.html
    """
    required_options = [keypoint_id, comparison_id]
    if required_options.count(None) != len(required_options) - 1:
        raise click.UsageError(
            "Either '--keypoint-id' or '--comparison-id' is required"
        )

    rule, background_rule = _parse_rule_and_bg_rule(rule_str, bg_rule_str, rule_file)
    client = get_client(state)

    if is_download is None:
        is_download = state.is_download
    if is_download is None:
        is_download = click.confirm("Download the drawn file?")
    if not is_download:
        args = click.get_os_args()
        options = check_download_options(args)
        echo_invalid_option_warning("downloading the file", options)

    try:
        drawing_id = client.draw_keypoint(
            keypoint_id=keypoint_id,
            comparison_id=comparison_id,
            rule=rule,
            background_rule=background_rule,
        )
        echo(f"Drawing started. (drawing id: {color_id(drawing_id)})")

        if state.use_spinner:
            with yaspin(text="Processing..."):
                response = client.wait_for_drawing(drawing_id)
        else:
            response = client.wait_for_drawing(drawing_id)
    except RequestsError as e:
        raise ClickException(str(e))

    if response.status == "SUCCESS":
        echo_success("Drawing is complete.")
    elif response.status == "TIMEOUT":
        raise ClickException("Drawing is timed out.")
    else:
        raise ClickException("Drawing failed.")

    echo()
    if is_download:
        ctx.invoke(download, drawing_id=drawing_id, **kwargs)
    else:
        message = dedent(
            f"""\
            Skip download. To download it, run the following command.

            "{state.cli_name} download {drawing_id}"
            """
        )
        echo(message)


def _parse_rule_and_bg_rule(
    rule_str: Optional[str],
    bg_rule_str: Optional[str],
    rule_file: Optional[io.TextIOWrapper],
) -> Tuple[Optional[Union[list, dict]], Optional[Union[list, dict]]]:
    rule, bg_rule = None, None

    if rule_file is not None:
        if rule_str is not None:
            raise click.UsageError(
                '"--rule" and "--rule-file" options cannot be used at the same time.'
            )
        if bg_rule_str is not None:
            raise click.UsageError(
                '"--bg-rule" and "--rule-file" options cannot be used at the same time.'
            )

        rule = parse_rule(rule_file.read())

        if isinstance(rule, dict):
            rule_dict: dict = rule
            rule_keys = rule_dict.keys() & {"rule", "backgroundRule"}
            if len(rule_keys) > 0:
                if len(set(rule) - rule_keys) > 0:
                    raise ClickException("Rule format is invalid.")

                rule = rule_dict.get("rule")
                rule = rule_dict.get("backgroundRule")
    else:
        if rule_str is not None:
            rule = parse_rule(rule_str)
        if bg_rule_str is not None:
            bg_rule = parse_rule(bg_rule_str)

    return rule, bg_rule
