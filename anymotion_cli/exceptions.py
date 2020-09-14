from typing import Any, Optional

import click
from click._compat import get_text_stderr


class ClickException(click.ClickException):
    """A click exception."""

    def show(self, file: Optional[Any] = None) -> None:
        """Show error message."""
        if file is None:
            file = get_text_stderr()
        error = click.style("Error", fg="red")
        click.echo(f"{error}: {self.format_message()}", file=file)


class SettingsException(Exception):
    """Base class for exceptions in the Settings module."""


class SettingsValueError(SettingsException):
    """Raised when settings value is invalid."""


class HelpColorsException(Exception):
    """Raised when unknown color is given."""


class InternalCommandException(Exception):
    """Base class for exceptions in the internal exception."""


class ExitReplException(InternalCommandException):
    """Exit repl."""
