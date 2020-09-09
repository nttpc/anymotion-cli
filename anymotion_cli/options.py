from typing import Any, Callable, Optional

import click

from .click_custom import custom_option
from .state import State


def verbose_option(f: Callable) -> Callable:
    """Set verbose option."""

    def callback(ctx: click.Context, param: Any, value: bool) -> bool:
        state = ctx.ensure_object(State)
        state.verbose = value
        return value

    return custom_option(
        "-v",
        "--verbose",
        is_flag=True,
        expose_value=False,
        help="Enables verbosity.",
        callback=callback,
        is_global=True,
    )(f)


def profile_option(f: Callable) -> Callable:
    """Set profile option."""

    def callback(ctx: click.Context, param: Any, value: Optional[str]) -> Optional[str]:
        state = ctx.ensure_object(State)
        if value:
            state.profile = value
        return value

    return custom_option(
        "--profile",
        expose_value=False,
        help="Use a specific profile from your config file.",
        callback=callback,
        is_global=True,
    )(f)


def common_options(f: Callable) -> Callable:
    """Set common options."""
    f = verbose_option(f)
    f = profile_option(f)
    return f
