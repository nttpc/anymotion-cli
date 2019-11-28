from pathlib import Path
from tempfile import TemporaryDirectory

from encore_api_cli.config import Config


def test_設定情報の初期値を取得できること(mocker):
    with TemporaryDirectory(prefix='pytest_') as tmp_dir:
        home_mock = mocker.MagicMock(return_value=Path(tmp_dir))
        mocker.patch('pathlib.Path.home', home_mock)

        config = Config()

        assert config.url == 'https://api.anymotion.jp/api/v1/'
        assert config.token is None
