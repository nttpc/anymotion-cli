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
            error_msg = str(error)
            original_cmd_name = click.utils.make_str(args[0])
            matches = difflib.get_close_matches(
                original_cmd_name,
                self.list_commands(ctx),
                self.max_suggestions,
                self.cutoff,
            )
            if matches:
                error_msg += "\n\nDid you mean one of these?\n\t"
                error_msg += "\n\t".join(matches)

            raise UsageError(error_msg, error.ctx)
