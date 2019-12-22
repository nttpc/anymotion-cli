import configparser
from pathlib import Path


class Config(object):
    def __init__(self, profile='default'):
        config = configparser.ConfigParser()

        self.config_dir = Path.home() / '.anymotion'
        self.config_file = self.config_dir / 'config'
        if self.config_file.exists():
            config.read(self.config_file)

        self.url = 'https://api.anymotion.jp/api/v1/'
        self.token = None
        if profile in config.sections():
            self.url = config[profile].get('anymotion_api_url', self.url)
            self.token = config[profile].get('anymotion_access_token',
                                             self.token)

        self.config = config
        self.profile = profile

        if self.token is None:
            self.is_ok = False
        else:
            self.is_ok = True

    def update(self):
        self.config[self.profile] = {
            'anymotion_api_url': self.url,
            'anymotion_access_token': self.token
        }
        self.config_dir.mkdir(exist_ok=True)
        with self.config_file.open('w') as f:
            self.config.write(f)

    def show(self):
        for section in self.config.sections():
            print(f'[{section}]')
            print('anymotion_api_url', '=',
                  self.config[section].get('anymotion_api_url'))
            print('anymotion_access_token', '=',
                  self.config[section].get('anymotion_access_token'))
            print()
