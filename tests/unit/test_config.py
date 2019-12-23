from pathlib import Path

from encore_api_cli.config import Config


class Test_設定ファイルが存在しない場合(object):

    def test_設定情報の初期値を取得できること(self, mocker, tmpdir):
        tmpdir = Path(tmpdir)
        mocker.patch('pathlib.Path.home', mocker.MagicMock(return_value=tmpdir))

        config = Config()

        assert config.url == 'https://api.customer.jp/'
        assert config.client_id is None
        assert config.client_secret is None

    def test_設定ファイルを作成できること(self, mocker, tmpdir):
        tmpdir = Path(tmpdir)
        mocker.patch('pathlib.Path.home', mocker.MagicMock(return_value=tmpdir))

        config_file_path = tmpdir / '.anymotion' / 'config'
        assert not config_file_path.exists()

        config = Config()
        config.url = 'http://api.example.com/'
        config.client_id = 'client_id'
        config.client_secret = 'client_secret'
        config.update()

        assert config_file_path.exists()


class Test_設定ファイルが存在する場合(object):

    def test_設定ファイルの値を取得できること(self, mocker, tmpdir):
        tmpdir = Path(tmpdir)
        mocker.patch('pathlib.Path.home', mocker.MagicMock(return_value=tmpdir))

        config_file_path = tmpdir / '.anymotion' / 'config'
        (tmpdir / '.anymotion').mkdir()
        config_file_path.write_text(
            '[default]\n'
            'anymotion_api_url = http://api.example.com/\n'
            'anymotion_client_id = client_id\n'
            'anymotion_client_secret = client_secret\n')

        config = Config()

        assert config.url == 'http://api.example.com/'
        assert config.client_id == 'client_id'
        assert config.client_secret == 'client_secret'

    def test_設定内容を表示できること(self, mocker, capfd, tmpdir):
        tmpdir = Path(tmpdir)
        mocker.patch('pathlib.Path.home', mocker.MagicMock(return_value=tmpdir))

        config_file_path = tmpdir / '.anymotion' / 'config'
        (tmpdir / '.anymotion').mkdir()
        config_file_path.write_text(
            '[default]\n'
            'anymotion_api_url = http://api.example.com/\n'
            'anymotion_client_id = client_id\n'
            'anymotion_client_secret = client_secret\n')

        config = Config()
        config.show()

        out, err = capfd.readouterr()
        assert out == '[default]\n' \
            'anymotion_api_url = http://api.example.com/\n' \
            'anymotion_client_id = client_id\n' \
            'anymotion_client_secret = client_secret\n\n'
        assert err == ''
