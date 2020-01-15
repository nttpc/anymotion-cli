import json
from pathlib import Path
from urllib.parse import urlparse

import click

from encore_api_cli.exceptions import ClickException
from encore_api_cli.options import common_options
from encore_api_cli.output import write_message, write_success
from encore_api_cli.state import pass_state
from encore_api_cli.utils import color_id, color_path, get_client


def draw_options(f):
    """Set draw options."""
    f = click.option("--no-download", is_flag=True, help="Disable download.")(f)
    f = click.option("--rule", help="Drawing rules.")(f)
    f = click.option(
        "-o",
        "--out_dir",
        default=".",
        type=click.Path(),
        show_default=True,
        help="Path of directory to output drawn file.",
    )(f)
    return f


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.command()
@click.argument("keypoint_id", type=int)
@draw_options
@common_options
@pass_state
def draw(state, keypoint_id, out_dir, rule, no_download):
    """Draw keypoints on uploaded movie or image."""
    c = get_client(state)
    drawing_id = c.draw_keypoint(keypoint_id, rule=_parse_rule(rule))
    write_message(f"Drawing started. (drawing_id: {color_id(drawing_id)})")

    # TODO: invoke download command
    status, url = c.wait_for_drawing(drawing_id)
    if status == "SUCCESS":
        write_success("Drawing is complete.")
        if no_download:
            return

        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / Path(urlparse(url).path).name

        if path.exists():
            write_message(f"File already exists: {color_path(path)}")
            if not click.confirm("Do you want to overwrite?"):
                write_message("Skip download.")
                return
        c.download(url, path)
        write_message(f"Downloaded the file to {color_path(path)}.")
    elif status == "TIMEOUT":
        write_message("Drawing is timed out.")
    else:
        write_message("Drawing failed.")


def _parse_rule(rule):
    if rule is None:
        return rule

    try:
        rule = json.loads(rule)
    except json.decoder.JSONDecodeError:
        raise ClickException("Rule format is invalid. Must be in JSON format.")

    if not isinstance(rule, list):
        raise ClickException("Rule format is invalid. Must be in list format.")

    return rule
