import click

from .client import Client
from .config import Config


def get_client(profile):
    config = Config(profile)
    if not config.is_ok:
        message = ' '.join([
            'The access token is invalid or not set.',
            'Run "encore configure" to set token.'
        ])
        raise click.ClickException(message)
    return Client(config.token, config.url)
