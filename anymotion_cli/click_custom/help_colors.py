import click


class HelpColorsFormatter(click.HelpFormatter):
    """Colorize help formatter."""

    def __init__(self, headers_color, options_color, *args, **kwargs):
        self.headers_color = headers_color
        self.options_color = options_color
        super(HelpColorsFormatter, self).__init__(*args, **kwargs)

    def write_usage(self, prog, args="", prefix="Usage: "):  # noqa: D102
        colorized_prefix = click.style(prefix, fg=self.headers_color)
        super(HelpColorsFormatter, self).write_usage(
            prog, args, prefix=colorized_prefix
        )

    def write_heading(self, heading):  # noqa: D102
        colorized_heading = click.style(heading, fg=self.headers_color)
        super(HelpColorsFormatter, self).write_heading(colorized_heading)

    def write_dl(self, rows, **kwargs):  # noqa: D102
        colorized_rows = [
            (click.style(row[0], fg=self.options_color), row[1]) for row in rows
        ]
        super(HelpColorsFormatter, self).write_dl(colorized_rows, **kwargs)


class HelpColorsMixin(object):
    """Mixin class to provide colored help."""

    def __init__(
        self, help_headers_color=None, help_options_color=None, *args, **kwargs
    ):
        self.help_headers_color = help_headers_color
        self.help_options_color = help_options_color
        super(HelpColorsMixin, self).__init__(*args, **kwargs)

    def get_help(self, ctx):  # noqa: D102
        formatter = HelpColorsFormatter(
            width=ctx.terminal_width,
            max_width=ctx.max_content_width,
            headers_color=self.help_headers_color,
            options_color=self.help_options_color,
        )
        self.format_help(ctx, formatter)
        return formatter.getvalue().rstrip("\n")
