from typing import Any, Optional

import click
from click._compat import get_text_stderr


class ClickException(click.ClickException):
    def show(self, file: Optional[Any] = None) -> None:
        """Show error message."""
        if file is None:
            file = get_text_stderr()
        click.echo(
            f"{click.style('Error', fg='red')}: {self.format_message()}", file=file
        )


class ClientException(Exception):
    pass


class InvalidFileType(ClientException):
    pass


class RequestsError(ClientException):
    pass


class SettingsException(Exception):
    pass


class SettingsValueError(SettingsException):
    pass
