import click


class State(object):
    def __init__(self) -> None:
        self.verbose = False
        self.profile = "default"
        # self.data = {}


pass_state = click.make_pass_decorator(State, ensure=True)
