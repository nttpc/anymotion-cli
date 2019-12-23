import configparser
from pathlib import Path
import textwrap


class Config(object):

    def __init__(self, profile='default'):
        config = configparser.ConfigParser()

        # TODO(y_kumiha): 環境変数で設定ディレクトリを変更できるようにする
        self.config_dir = Path.home() / '.anymotion'
        self.config_file = self.config_dir / 'config'
        if self.config_file.exists():
            config.read(self.config_file)

        self.url = 'https://api.customer.jp/'
        self.client_id, self.client_secret = None, None
        if profile in config.sections():
            self.url = config[profile].get('anymotion_api_url', self.url)
            self.client_id = config[profile].get('anymotion_client_id',
                                                 self.client_id)
            self.client_secret = config[profile].get('anymotion_client_secret',
                                                     self.client_secret)

        self.config = config
        self.profile = profile

        if self.client_id is None or self.client_secret is None:
            self.is_ok = False
        else:
            self.is_ok = True

    def update(self):
        # TODO(y_kumiha): self.url の最後に / がない場合の処理
        self.config[self.profile] = {
            'anymotion_api_url': self.url,
            'anymotion_client_id': self.client_id,
            'anymotion_client_secret': self.client_secret
        }
        self.config_dir.mkdir(exist_ok=True)
        with self.config_file.open('w') as f:
            self.config.write(f)

    def show(self):
        for section_name in self.config.sections():
            section = self.config[section_name]

            url = section.get('anymotion_api_url')
            client_id = section.get('anymotion_client_id')
            client_secret = section.get('anymotion_client_secret')

            print(
                textwrap.dedent(f"""\
                    [{section_name}]
                    anymotion_api_url = {url}
                    anymotion_client_id = {client_id}
                    anymotion_client_secret = {client_secret}
            """))
