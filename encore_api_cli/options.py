import click

from encore_api_cli.state import State


def verbose_option(f):
    def callback(ctx, param, value):
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


def profile_option(f):
    def callback(ctx, param, value):
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


def format_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.format = value
        return value

    return click.option(
        "-f",
        "--format",
        default="json",
        show_default=True,
        expose_value=False,
        help="The formatting style for command output.",
        callback=callback,
    )(f)


def common_options(f):
    # f = verbose_option(f)
    f = profile_option(f)
    # f = format_option(f)
    return f
