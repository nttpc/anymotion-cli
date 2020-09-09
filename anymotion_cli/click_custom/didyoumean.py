# Copyright (c) 2020 NTTPC Communications, Inc.
# See https://github.com/nttpc/anymotion-cli/blob/master/LICENSE.

# Classes under this library were originally taken from click-didyoumean,
# Copyright (c) 2016 Timo Furrer.
# These Classes are licensed under the MIT license.
# See https://github.com/click-contrib/click-didyoumean/blob/master/LICENSE.


import difflib

import click
from click import UsageError


class DYMMixin(object):
    """Mixin class to provide `Did you mean ...` suggestions."""

    def __init__(self, *args, **kwargs):
        self.max_suggestions = kwargs.pop("max_suggestions", 3)
        self.cutoff = kwargs.pop("cutoff", 0.5)
        super(DYMMixin, self).__init__(*args, **kwargs)

    def resolve_command(self, ctx, args):  # noqa: D102
        try:
            return super(DYMMixin, self).resolve_command(ctx, args)
        except UsageError as error:
            cmd_name = click.utils.make_str(args[0])
            cmd_list = self.list_commands(ctx)
            error_msg = self._create_error_msg(str(error), cmd_name, cmd_list)
            raise UsageError(error_msg, error.ctx)

    def _create_error_msg(self, error_msg: str, cmd_name: str, cmd_list: list) -> str:
        matches = difflib.get_close_matches(
            cmd_name,
            cmd_list,
            self.max_suggestions,
            self.cutoff,
        )
        if len(matches) > 1:
            error_msg += "\n\nDid you mean one of these?\n\t"
            error_msg += "\n\t".join(matches)
        elif len(matches) > 0:
            error_msg += f"\n\nDid you mean this?\n\t{matches[0]}"

        return error_msg
