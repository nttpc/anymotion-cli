from pathlib import Path
from urllib.parse import urljoin

import pytest

from encore_api_cli.client import Client

base_url = 'http://api.example.com/'
api_url = 'http://api.example.com/anymotion/v1/'
oauth_url = 'http://api.example.com/v1/oauth/accesstokens'


@pytest.mark.parametrize('expected_media_type,path', [('image', 'image.jpg'),
                                                      ('movie', 'movie.mp4')])
def test_ファイルをS3にアップロードできること(mocker, requests_mock, expected_media_type, path):
    expected_media_id = 1
    upload_url = 'http://upload_url.example.com'

    file_mock = mocker.mock_open(read_data=b'image data')
    mocker.patch('pathlib.Path.open', file_mock)

    requests_mock.post(oauth_url, json={'accessToken': 'token'})
    requests_mock.post(urljoin(api_url, f'{expected_media_type}s/'),
                       json={
                           'id': expected_media_id,
                           'upload_url': upload_url
                       })
    requests_mock.put(upload_url)

    c = Client('client_id', 'client_secret', base_url)
    media_id, media_type = c.upload_to_s3(path)

    assert media_id == expected_media_id
    assert media_type == expected_media_type


def test_キーポイント抽出ができること(requests_mock, capfd):
    keypoint_id = 1

    requests_mock.post(oauth_url, json={'accessToken': 'token'})
    requests_mock.post(urljoin(api_url, 'keypoints/'), json={'id': keypoint_id})
    requests_mock.get(urljoin(api_url, f'keypoints/{keypoint_id}/'),
                      json={'exec_status': 'SUCCESS'})

    c = Client('client_id', 'client_secret', base_url)
    c.extract_keypoint(image_id=1)

    out, err = capfd.readouterr()
    assert out == f'Extract keypoint (keypoint_id: {keypoint_id})\n\n' \
                  'Keypoint extraction is complete.\n'
    assert err == ''


def test_キーポイントデータを取得できること(requests_mock):
    keypoint_id = 1
    expected_keypoint = '[]'
    # expected_keypoint = '[{"0": [1, 2]}]'

    requests_mock.post(oauth_url, json={'accessToken': 'token'})
    requests_mock.get(urljoin(api_url, f'keypoints/{keypoint_id}/'),
                      json={
                          'exec_status': 'SUCCESS',
                          'keypoint': expected_keypoint
                      })

    c = Client('client_id', 'client_secret', base_url)
    keypoint = c.get_keypoint(keypoint_id)

    assert keypoint == expected_keypoint


def test_解析結果を取得できること(requests_mock):
    analysis_id = 1
    expected_result = '[]'

    requests_mock.post(oauth_url, json={'accessToken': 'token'})
    requests_mock.get(urljoin(api_url, f'analyses/{analysis_id}/'),
                      json={
                          'exec_status': 'SUCCESS',
                          'result': expected_result
                      })

    c = Client('client_id', 'client_secret', base_url)
    result = c.get_analysis(analysis_id)

    assert result == expected_result


def test_キーポイントを描画できること(requests_mock):
    keypoint_id = 1
    drawing_id = 1
    expected_drawing_url = 'http://drawing_url.example.com'

    requests_mock.post(oauth_url, json={'accessToken': 'token'})

    requests_mock.post(f'{api_url}drawings/', json={'id': drawing_id})
    requests_mock.get(f'{api_url}drawings/{drawing_id}/',
                      json={
                          'exec_status': 'SUCCESS',
                          'drawing_url': expected_drawing_url
                      })

    c = Client('client_id', 'client_secret', base_url)
    drawing_url = c.draw_keypoint(keypoint_id)

    assert drawing_url == expected_drawing_url


def test_キーポイントの解析ができること(requests_mock):
    keypoint_id = 1
    rule_id = 1
    analysis_id = 1
    expected_result = '[]'

    requests_mock.post(oauth_url, json={'accessToken': 'token'})
    requests_mock.post(f'{api_url}analyses/', json={'id': analysis_id})
    requests_mock.get(f'{api_url}analyses/{analysis_id}/',
                      json={
                          'exec_status': 'SUCCESS',
                          'result': expected_result
                      })

    c = Client('client_id', 'client_secret', base_url)
    result = c.analyze_keypoint(keypoint_id, rule_id)

    assert result == expected_result


def test_ファイルをダウンロードできること(mocker, requests_mock, tmpdir):
    tmpdir = Path(tmpdir)
    url = 'http://download.example.com/image.jpg'
    path = tmpdir / 'image.jpg'

    requests_mock.post(oauth_url, json={'accessToken': 'token'})
    requests_mock.get(url, content=b'image data')

    mkdir_mock = mocker.MagicMock()
    mocker.patch('pathlib.Path.mkdir', mkdir_mock)

    assert not path.exists()

    c = Client('client_id', 'client_secret', base_url)
    c.download(url, tmpdir)

    assert path.exists()
