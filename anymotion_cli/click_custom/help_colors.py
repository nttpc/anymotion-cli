# Copyright (c) 2020 NTTPC Communications, Inc.
# See https://github.com/nttpc/anymotion-cli/blob/master/LICENSE.

# Classes under this library were originally taken from click-help-colors,
# Copyright (c) 2016 Roman Tonkonozhko.
# These Classes are licensed under the MIT license.
# See https://github.com/click-contrib/click-help-colors/blob/master/LICENSE.txt.


from typing import Tuple

import click

from .formatting import SeparateHelpFormatter


class HelpColorsFormatter(SeparateHelpFormatter):
    """Colorize help formatter."""

    def __init__(self, headers_color: str, options_color: str, *args, **kwargs):
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
        colorized_rows = []
        for row in rows:
            option, metavar = _split_option(row[0])
            colorized_option = click.style(option, fg=self.options_color)
            if metavar:
                colorized_option += " " + metavar
            colorized_rows.append((colorized_option, row[1]))
        super(HelpColorsFormatter, self).write_dl(colorized_rows, **kwargs)


class HelpColorsMixin(object):
    """Mixin class to provide colorized help."""

    def __init__(
        self, help_headers_color=None, help_options_color=None, *args, **kwargs
    ):
        self.help_headers_color = help_headers_color
        self.help_options_color = help_options_color
        super(HelpColorsMixin, self).__init__(*args, **kwargs)

    def get_help(self, ctx):  # noqa: D102
        formatter = HelpColorsFormatter(
            headers_color=self.help_headers_color,
            options_color=self.help_options_color,
        )
        self.format_help(ctx, formatter)
        return formatter.getvalue()


def _split_option(option: str) -> Tuple[str, str]:
    splited = option.split(" ")
    if len(splited) > 0 and splited[-1].isupper():
        metavar = splited.pop()
        return " ".join(splited), metavar
    else:
        return option, ""
