from typing import Optional

import click

from .output import is_show


class State(object):
    """Manage state."""

    def __init__(self) -> None:
        self.verbose = False
        self.profile = "default"
        self.cli_name = "amcli"
        self.pager_length = 10

        self.is_download: Optional[bool] = None
        self.is_open: Optional[bool] = None

    @property
    def use_spinner(self) -> bool:
        """Flag to use spinner.

        True if:
            - verbose option is not set
            - output to terminal
            - ANYMOTION_USE_SPINNER is true or not set
        """
        from .utils import get_bool_env

        env = get_bool_env("ANYMOTION_USE_SPINNER", True)
        return not self.verbose and is_show() and env


pass_state = click.make_pass_decorator(State, ensure=True)
