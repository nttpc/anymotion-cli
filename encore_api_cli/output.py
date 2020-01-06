import functools
import json
import sys
from typing import Any, Optional

import click
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer
from yaspin.core import Yaspin

STDOUT_ISATTY = sys.stdout.isatty()


def write_message(
    message: Optional[str] = None,
    message_type: Optional[str] = None,
    stdout_isatty: bool = STDOUT_ISATTY,
) -> None:
    """Output message only for terminal."""
    if not stdout_isatty:
        return

    if message_type == "success" and message is not None:
        message = f"{click.style('Success', fg='green')}: " + message
        click.echo(message)
    else:
        click.echo(message)


def write_success(message: str, **kwargs: Any) -> None:
    """Output success message."""
    write_message(message, message_type="success", **kwargs)


def write_json_data(
    data: object, sort_keys: bool = True, stdout_isatty: bool = STDOUT_ISATTY,
) -> None:
    """Output json data."""
    if stdout_isatty:
        click.echo()

    body = json.dumps(data, sort_keys=sort_keys, indent=2)
    body = highlight(body, JsonLexer(), TerminalFormatter())
    click.echo(body)


def write_http(
    url: str,
    method: str,
    headers: Optional[dict] = None,
    data: Optional[object] = None,
    **kwargs: Any,
) -> None:
    """Output http request."""
    url = click.style(url, fg="cyan")
    method = click.style(method, fg="green")
    click.echo(f"{method} {url}")

    if headers is not None:
        for key, value in headers.items():
            key = click.style(key, fg="cyan")
            click.echo(f"{key}: {value}")

    if data is not None:
        write_json_data(data, **kwargs)


def spin(stdout_isatty: bool = STDOUT_ISATTY, *args, **kwargs):
    """Display spinner in terminal."""
    if stdout_isatty:
        return Yaspin(*args, **kwargs)
    else:
        return Nospin()


class Nospin(object):
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self) -> None:
        pass

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        pass

    def __call__(self, fn):
        """Call."""

        @functools.wraps(fn)
        def inner(*args, **kwargs):
            with self:
                return fn(*args, **kwargs)

        return inner
