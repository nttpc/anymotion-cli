from platform import python_version
from typing import Any, Callable, Optional

import click

from .click_custom import custom_option
from .state import State


def version_option(version, *param_decls, **kwargs):
    """Add --version option."""

    def callback(ctx, param, value):
        if not value or ctx.resilient_parsing:
            return

        nonlocal version

        cli_name = str(ctx.find_root().info_name)
        version = click.style(version, fg="cyan")
        message = f"{cli_name} version {version}"

        if value > 1:
            message += (
                f" (anymotion-sdk {_get_sdk_version()}, Python {python_version()})"
            )

        click.echo(message)
        ctx.exit()

    if not param_decls:
        param_decls = ("--version",)

    kwargs.setdefault("count", True)
    kwargs.setdefault("expose_value", False)
    kwargs.setdefault("is_eager", True)
    kwargs.setdefault(
        "help", "Show the version and exit. When given -VV, show more information."
    )
    kwargs["callback"] = callback

    return click.option(*param_decls, **kwargs)


def _get_sdk_version():
    try:
        from importlib import metadata
    except ImportError:
        import importlib_metadata as metadata

    package_name = "anymotion-sdk"
    try:
        version = metadata.version(package_name)
    except metadata.PackageNotFoundError:
        raise RuntimeError(f"{package_name!r} is not installed.")

    return version


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
