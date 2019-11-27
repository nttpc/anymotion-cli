import pytest

from encore_api_cli.client import Client


@pytest.mark.parametrize('expected_media_type,path', [('image', 'image.jpg'),
                                                      ('movie', 'movie.mp4')])
def test_ファイルをS3にアップロードできること(mocker, requests_mock, expected_media_type, path):
    expected_media_id = 1

    base_url = 'http://api.example.com'
    upload_url = 'http://upload_url.example.com'

    file_mock = mocker.mock_open(read_data=b'image data')
    mocker.patch('pathlib.Path.open', file_mock)

    requests_mock.post(f'{base_url}/{expected_media_type}s/',
                       json={
                           'id': expected_media_id,
                           'upload_url': upload_url
                       })
    requests_mock.put(upload_url)

    c = Client('token', base_url)
    media_id, media_type = c.upload_to_s3(path)

    assert media_id == expected_media_id
    assert media_type == expected_media_type
