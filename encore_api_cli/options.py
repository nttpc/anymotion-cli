from typing import Any, Callable

import click

from encore_api_cli.state import State


def verbose_option(f: Callable) -> Callable:
    """Set verbose option."""

    def callback(ctx: click.core.Context, param: Any, value: bool) -> bool:
        state = ctx.ensure_object(State)
        state.verbose = value
        return value

    return click.option(
        "-v",
        "--verbose",
        is_flag=True,
        expose_value=False,
        help="Enables verbosity.",
        callback=callback,
    )(f)


def profile_option(f: Callable) -> Callable:
    """Set profile option."""

    def callback(ctx: click.core.Context, param: Any, value: str) -> str:
        state = ctx.ensure_object(State)
        state.profile = value
        return value

    return click.option(
        "--profile",
        default="default",
        expose_value=False,
        help="Use a specific profile from your credential file.",
        callback=callback,
    )(f)


def common_options(f: Callable) -> Callable:
    """Set common options."""
    f = profile_option(f)
    f = verbose_option(f)
    return f