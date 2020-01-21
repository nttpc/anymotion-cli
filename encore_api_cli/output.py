import functools
import json
import os
import sys
from distutils.util import strtobool
from typing import Any, Callable, Optional, Union

import click
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer
from yaspin.core import Yaspin


def echo(message: Optional[str] = None) -> None:
    """Output message."""
    if _is_show():
        click.echo(message)


def echo_success(message: str) -> None:
    """Output success message."""
    if _is_show():
        echo(f"{click.style('Success', fg='green')}: {message}")


def echo_json(data: object, sort_keys: bool = False) -> None:
    """Output json data."""
    if _is_show():
        click.echo()

    body = json.dumps(data, sort_keys=sort_keys, indent=2)
    body = highlight(body, JsonLexer(), TerminalFormatter())
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


class Nospin(object):
    def __init__(self, *args: Any, **kwargs: Any):
        pass

    def __enter__(self) -> None:
        pass

    def __exit__(self, *exc: Any) -> None:
        pass

    def __call__(self, fn: Callable) -> Callable:
        """Call."""

        @functools.wraps(fn)
        def inner(*args: Any, **kwargs: Any) -> Callable:
            with self:
                return fn(*args, **kwargs)

        return inner


def spin(*args: Any, **kwargs: Any) -> Union[Yaspin, Nospin]:
    """Display spinner in terminal."""
    if _is_show():
        return Yaspin(*args, **kwargs)
    else:
        return Nospin()


def _is_show() -> bool:
    env = os.getenv("STDOUT_ISSHOW")
    if env is None:
        return sys.stdout.isatty()
    else:
        try:
            return bool(strtobool(env))
        except ValueError:
            return sys.stdout.isatty()
