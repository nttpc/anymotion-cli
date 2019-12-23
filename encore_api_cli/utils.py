import click

from .client import Client
from .config import Config


def get_client(profile):
    config = Config(profile)
    if not config.is_ok:
        message = ' '.join([
            'The credentials is invalid or not set.',
            'Run "encore configure" to set credentials.'
        ])
        raise click.ClickException(message)
    return Client(config.client_id, config.client_secret, config.url)
