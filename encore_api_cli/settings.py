import configparser
import os
from pathlib import Path

# default values
BASE_URL = 'https://api.customer.jp/'
POLLING_INTERVAL = 10
TIMEOUT = 600


class Settings(object):
    def __init__(self, profile_name='default'):
        self.profile_name = profile_name

        self.settings_dir = self._get_dir()
        self.settings_dir.mkdir(exist_ok=True)

        # read config and credentials files
        self.config = configparser.ConfigParser()
        self.config_file = self.settings_dir / 'config'
        if self.config_file.exists():
            self.config.read(self.config_file)

        self.credentials = configparser.ConfigParser()
        self.credentials_file = self.settings_dir / 'credentials'
        if self.credentials_file.exists():
            self.credentials.read(self.credentials_file)

        # set values
        self._set_default_values()
        self._set_config_from_file(profile_name)
        self._set_credentials_from_file(profile_name)
        self._set_credentials_from_env()

    def is_ok(self):
        return self.client_id is not None and self.client_secret is not None

    def write_config(self):
        """Update config file.

        Update only when different from default value.
        """
        if self.url == BASE_URL:
            return

        self.config[self.profile_name] = {
            'anymotion_api_url': self.url,
        }
        with self.config_file.open('w') as f:
            self.config.write(f)

    def write_credentials(self):
        """Update credentials file."""
        if not self.is_ok():
            raise ValueError('client_id or client_secret is invald.')

        self.credentials[self.profile_name] = {
            'anymotion_client_id': self.client_id,
            'anymotion_client_secret': self.client_secret
        }
        with self.credentials_file.open('w') as f:
            self.credentials.write(f)

    def _get_dir(self):
        root_dir = os.getenv('ANYMOTION_ROOT', Path.home())
        return Path(root_dir) / '.anymotion'

    def _set_default_values(self):
        self.url = BASE_URL
        self.interval = POLLING_INTERVAL
        self.timeout = TIMEOUT
        self.client_id = None
        self.client_secret = None

    def _set_config_from_file(self, profile_name):
        if profile_name not in self.config.sections():
            return
        profile = self.config[profile_name]

        url = profile.get('anymotion_api_url')
        if url is not None:
            self.url = url

        interval = profile.getint('polling_interval')
        if interval is not None:
            self.interval = interval

        timeout = profile.getint('timeout')
        if timeout is not None:
            self.timeout = timeout

    def _set_credentials_from_file(self, profile_name):
        if profile_name not in self.credentials.sections():
            return
        profile = self.credentials[profile_name]

        client_id = profile.get('anymotion_client_id')
        if client_id is not None:
            self.client_id = client_id

        client_secret = profile.get('anymotion_client_secret')
        if client_secret is not None:
            self.client_secret = client_secret

    def _set_credentials_from_env(self):
        client_id = os.getenv('ANYMOTION_CLIENT_ID')
        if client_id is not None:
            self.client_id = client_id

        client_secret = os.getenv('ANYMOTION_CLIENT_SECRET')
        if client_secret is not None:
            self.client_secret = client_secret
