import click

from .didyoumean import DYMMixin
from .help_colors import HelpColorsMixin


class CustomMixin(DYMMixin, HelpColorsMixin):
    """Mixin class for DYMMixin and HelpColorsMixin."""

    def __init__(self, *args, **kwargs):
        super(CustomMixin, self).__init__(*args, **kwargs)


class CustomGroup(CustomMixin, click.Group):
    """Custom click Group."""

    def __init__(self, *args, **kwargs):
        super(CustomGroup, self).__init__(*args, **kwargs)

    def command(self, *args, **kwargs):  # noqa: D102
        kwargs.setdefault("cls", CustomCommand)
        kwargs.setdefault("help_headers_color", self.help_headers_color)
        kwargs.setdefault("help_options_color", self.help_options_color)
        return super(CustomGroup, self).command(*args, **kwargs)

    def group(self, *args, **kwargs):  # noqa: D102
        kwargs.setdefault("cls", CustomGroup)
        kwargs.setdefault("help_headers_color", self.help_headers_color)
        kwargs.setdefault("help_options_color", self.help_options_color)
        return super(CustomGroup, self).group(*args, **kwargs)


class CustomCommand(CustomMixin, click.Command):
    """Custom click Command."""

    def __init__(self, *args, **kwargs):
        super(CustomCommand, self).__init__(*args, **kwargs)


class CustomCommandCollection(CustomMixin, click.CommandCollection):
    """Custom click CommandCollection."""

    def __init__(self, *args, **kwargs):
        super(CustomCommandCollection, self).__init__(*args, **kwargs)
