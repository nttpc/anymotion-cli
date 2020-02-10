import click

from .output import is_show
from .utils import get_bool_env


class State(object):
    """Manage state."""

    def __init__(self) -> None:
        self.verbose = False
        self.profile = "default"
        self.cli_name = "amcli"
        self.pager_length = 10

    @property
    def use_spinner(self) -> bool:
        """Flag to use spinner.

        True if:
            - verbose option is set
            - output ot terminal
            - ANYMOTION_USE_SPINNER is true or not set
        """
        env = get_bool_env("ANYMOTION_USE_SPINNER", True)
        return not self.verbose and is_show() and env


pass_state = click.make_pass_decorator(State, ensure=True)
