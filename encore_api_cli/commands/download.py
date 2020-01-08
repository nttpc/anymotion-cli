from pathlib import Path
from textwrap import dedent
from urllib.parse import urlparse

import click

from encore_api_cli.options import common_options
from encore_api_cli.output import write_message
from encore_api_cli.state import State, pass_state
from encore_api_cli.utils import color_path, get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.command()
@click.argument("drawing_id", type=int)
@click.option(
    "-o",
    "--out_dir",
    default=".",
    type=click.Path(exists=True),
    show_default=True,
    help="Path of directory to output drawn file.",
)
@common_options
@pass_state
@click.pass_context
def download(ctx, state: State, drawing_id: int, out_dir: str) -> None:
    """Download the drawn file."""
    c = get_client(state)
    status, url = c.wait_for_drawing(drawing_id)

    if status == "SUCCESS" and url is not None:
        path = Path(out_dir) / Path(str(urlparse(url).path)).name

        if path.exists():
            write_message(f"File already exists: {color_path(path)}")
            if not click.confirm("Do you want to overwrite?"):
                prog = ctx.find_root().info_name
                write_message(
                    dedent(
                        f"""\
                            Skip download. To download it, run the following command.

                            "{prog} download {drawing_id}"\
                        """
                    )
                )
                return
        c.download(url, path)
        write_message(f"Downloaded the file to {color_path(path)}.")
    else:
        write_message("Unable to download because drawing failed.")
