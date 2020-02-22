import io
from typing import Callable, Optional

import click
from click_help_colors import HelpColorsGroup
from yaspin import yaspin

from ..exceptions import ClickException
from ..options import common_options
from ..output import echo, echo_error, echo_success
from encore_sdk import RequestsError
from ..state import State, pass_state
from ..utils import color_id, get_client, parse_rule, get_name_from_drawing_id
from .download import check_download


def draw_options(f: Callable) -> Callable:
    """Set draw options."""
    f = click.option("--no-download", is_flag=True, help="Disable download.")(f)
    f = click.option("--rule", "rule_str", help="Drawing rules in JSON format.")(f)
    f = click.option(
        "--rule-file", type=click.File(), help="Drawing rules file in JSON format."
    )(f)
    f = click.option(
        "-o",
        "--out-dir",
        default=".",
        type=click.Path(exists=True, file_okay=False),
        show_default=True,
        help="Path of directory to output drawn file.",
    )(f)
    return f


@click.group(cls=HelpColorsGroup, help_options_color="cyan")
def cli() -> None:  # noqa: D103
    pass


@cli.command(short_help="Draw points and/or lines on uploaded movie or image.")
@click.argument("keypoint_id", type=int)
@draw_options
@common_options
@pass_state
def draw(
    state: State,
    keypoint_id: int,
    out_dir: str,
    rule_str: Optional[str],
    rule_file: Optional[io.TextIOWrapper],
    no_download: bool,
) -> None:
    """Draw points and/or lines on uploaded movie or image."""
    if rule_str is not None and rule_file is not None:
        raise click.UsageError(
            '"rule" and "rule-file" options cannot be used at the same time.'
        )

    rule = None
    if rule_str is not None:
        rule = parse_rule(rule_str)
    elif rule_file is not None:
        rule = parse_rule(rule_file.read())

    client = get_client(state)

    try:
        drawing_id = client.draw_keypoint(keypoint_id, rule=rule)
        echo(f"Drawing started. (drawing id: {color_id(drawing_id)})")

        if state.use_spinner:
            with yaspin(text="Processing..."):
                response = client.wait_for_drawing(drawing_id)
        else:
            response = client.wait_for_drawing(drawing_id)
        name = get_name_from_drawing_id(client, drawing_id)
    except RequestsError as e:
        raise ClickException(str(e))

    url = response.get("drawingUrl")
    if response.status == "SUCCESS" and url is not None:
        echo_success("Drawing is complete.")
        if no_download:
            return

        is_ok, message, path = check_download(out_dir, url, name)
        if is_ok:
            try:
                client.download(drawing_id, path)
            except RequestsError as e:
                raise ClickException(str(e))
        else:
            message = message % {"prog": state.cli_name, "drawing_id": drawing_id}
        echo(message)
    elif response.status == "TIMEOUT":
        echo_error("Drawing is timed out.")
    else:
        echo_error("Drawing failed.")
