import json
import sys
from typing import Optional

import click
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer


def echo(message: Optional[str] = None) -> None:
    """Output message."""
    if is_show():
        click.echo(message)


def echo_success(message: str) -> None:
    """Output success message."""
    if is_show():
        click.echo(f"{click.style('Success', fg='green')}: {message}")


def echo_json(data: object, sort_keys: bool = False, pager: bool = False) -> None:
    """Output json data."""
    if is_show():
        click.echo()

    body = json.dumps(data, sort_keys=sort_keys, indent=2)
    body = highlight(body, JsonLexer(), TerminalFormatter())

    if pager:
        click.echo_via_pager(body)
    else:
        click.echo(body)


def echo_request(
    url: str, method: str, headers: Optional[dict] = None, json: Optional[object] = None
) -> None:
    """Output http request."""
    url = click.style(url, fg="cyan")
    method = click.style(method, fg="green")
    click.echo(f"{method} {url}")

    if headers is not None:
        for key, value in headers.items():
            key = click.style(key, fg="cyan")
            click.echo(f"{key}: {value}")

    if json is not None:
        echo_json(json)

    click.echo()


def echo_response(
    status_code: int,
    reason: str,
    version: int,
    headers: Optional[dict],
    json: Optional[object],
) -> None:
    """Output http response."""
    status = click.style(str(status_code), fg="blue")
    reason = click.style(reason, fg="cyan")
    http_version = "HTTP"
    if version == 10:
        http_version = "HTTP/1.0"
    elif version == 11:
        http_version = "HTTP/1.1"
    http_version = click.style(http_version, fg="blue")
    click.echo(f"{http_version} {status} {reason}")

    if headers is not None:
        for key, value in headers.items():
            key = click.style(key, fg="cyan")
            click.echo(f"{key}: {value}")

    if json is not None:
        echo_json(json)

    click.echo()
    click.echo()


def is_show() -> bool:
    """Flag to show.

    It is True for terminals and False for pipes.
    If an environment variable has been set, its value is returned.
    """
    from encore_api_cli.utils import get_bool_env

    return get_bool_env("STDOUT_ISSHOW", sys.stdout.isatty())
