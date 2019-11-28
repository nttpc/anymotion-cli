from click.testing import CliRunner

from encore_api_cli.cli import cli

base_url = 'http://api.example.com'


def test_configure():
    runner = CliRunner()
    result = runner.invoke(cli, ['configure'])

    assert result.exit_code == 0


def test_configure_list(mocker):
    expected = ''

    config_mock = mocker.MagicMock()
    config_mock.return_value.show.return_value = expected
    mocker.patch('encore_api_cli.cli.Config', config_mock)

    runner = CliRunner()
    result = runner.invoke(cli, ['configure', 'list'])

    assert result.exit_code == 0
    assert result.output == expected


def test_image():
    runner = CliRunner()
    result = runner.invoke(cli, ['image'])

    assert result.exit_code == 0


def test_image_list(mocker, requests_mock):
    config_mock = mocker.MagicMock()
    config_mock.return_value.url = base_url
    mocker.patch('encore_api_cli.cli.Config', config_mock)

    requests_mock.get(f'{base_url}/images/',
                      json={
                          'data': '',
                          'next': None
                      })

    runner = CliRunner()
    result = runner.invoke(cli, ['image', 'list'])

    assert result.exit_code == 0
    assert result.output == '[]\n'


def test_movie():
    runner = CliRunner()
    result = runner.invoke(cli, ['movie'])

    assert result.exit_code == 0


def test_movie_list(mocker, requests_mock):
    config_mock = mocker.MagicMock()
    config_mock.return_value.url = base_url
    mocker.patch('encore_api_cli.cli.Config', config_mock)

    requests_mock.get(f'{base_url}/movies/', json={'data': '', 'next': None})

    runner = CliRunner()
    result = runner.invoke(cli, ['movie', 'list'])

    assert result.exit_code == 0
    assert result.output == '[]\n'


def test_keypoint():
    runner = CliRunner()
    result = runner.invoke(cli, ['keypoint'])

    assert result.exit_code == 0


def test_keypoint_list(mocker, requests_mock):
    config_mock = mocker.MagicMock()
    config_mock.return_value.url = base_url
    mocker.patch('encore_api_cli.cli.Config', config_mock)

    requests_mock.get(f'{base_url}/keypoints/', json={'data': '', 'next': None})

    runner = CliRunner()
    result = runner.invoke(cli, ['keypoint', 'list'])

    assert result.exit_code == 0
    assert result.output == '[]\n'


def test_analysis():
    runner = CliRunner()
    result = runner.invoke(cli, ['analysis'])

    assert result.exit_code == 0


def test_analysis_list(mocker, requests_mock):
    config_mock = mocker.MagicMock()
    config_mock.return_value.url = base_url
    mocker.patch('encore_api_cli.cli.Config', config_mock)

    requests_mock.get(f'{base_url}/analyses/', json={'data': '', 'next': None})

    runner = CliRunner()
    result = runner.invoke(cli, ['analysis', 'list'])

    assert result.exit_code == 0
    assert result.output == '[]\n'
