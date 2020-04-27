from typing import Any, Callable, Optional

import click

from .state import State


def verbose_option(f: Callable) -> Callable:
    """Set verbose option."""

    def callback(ctx: click.Context, param: Any, value: bool) -> bool:
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

    def callback(ctx: click.Context, param: Any, value: Optional[str]) -> Optional[str]:
        state = ctx.ensure_object(State)
        if value:
            state.profile = value
        return value

    return click.option(
        "--profile",
        expose_value=False,
        help="Use a specific profile from your config file.",
        callback=callback,
    )(f)


def common_options(f: Callable) -> Callable:
    """Set common options."""
    f = profile_option(f)
    f = verbose_option(f)
    return f
