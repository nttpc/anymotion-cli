from pathlib import Path
from tempfile import TemporaryDirectory

from encore_api_cli.config import Config


class Test_設定ファイルが存在しない場合(object):
    def test_設定情報の初期値を取得できること(self, mocker):
        with TemporaryDirectory(prefix='pytest_') as tmp_dir:
            home_mock = mocker.MagicMock(return_value=Path(tmp_dir))
            mocker.patch('pathlib.Path.home', home_mock)

            config = Config()

            assert config.url == 'https://api.anymotion.jp/api/v1/'
            assert config.token is None

    def test_設定ファイルを作成できること(self, mocker):
        with TemporaryDirectory(prefix='pytest_') as tmp_dir:
            home_mock = mocker.MagicMock(return_value=Path(tmp_dir))
            mocker.patch('pathlib.Path.home', home_mock)

            config_file_path = Path(tmp_dir) / '.anymotion' / 'config'
            assert not config_file_path.exists()

            config = Config()
            config.url = 'http://api.example.com/'
            config.token = 'token'
            config.update()

            assert config_file_path.exists()


class Test_設定ファイルが存在する場合(object):
    def test_設定ファイルの値を取得できること(self, mocker):
        with TemporaryDirectory(prefix='pytest_') as tmp_dir:
            home_mock = mocker.MagicMock(return_value=Path(tmp_dir))
            mocker.patch('pathlib.Path.home', home_mock)

            config_file_path = Path(tmp_dir) / '.anymotion' / 'config'
            (Path(tmp_dir) / '.anymotion').mkdir()
            config_file_path.write_text(
                '[default]\n'
                'anymotion_api_url = http://api.example.com/\n'
                'anymotion_access_token = token\n')

            config = Config()

            assert config.url == 'http://api.example.com/'
            assert config.token == 'token'

    def test_設定内容を表示できること(self, mocker, capfd):
        with TemporaryDirectory(prefix='pytest_') as tmp_dir:
            home_mock = mocker.MagicMock(return_value=Path(tmp_dir))
            mocker.patch('pathlib.Path.home', home_mock)

            config_file_path = Path(tmp_dir) / '.anymotion' / 'config'
            (Path(tmp_dir) / '.anymotion').mkdir()
            config_file_path.write_text(
                '[default]\n'
                'anymotion_api_url = http://api.example.com/\n'
                'anymotion_access_token = token\n')

            config = Config()
            config.show()

            out, err = capfd.readouterr()
            assert out == '[default]\n' \
                'anymotion_api_url = http://api.example.com/\n' \
                'anymotion_access_token = token\n\n'
            assert err == ''
