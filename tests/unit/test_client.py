from pathlib import Path
from urllib.parse import urljoin

import pytest

from encore_api_cli.client import Client
from encore_api_cli.exceptions import InvalidFileType


@pytest.fixture
def client(requests_mock):
    base_url = "http://api.example.com/"
    client = Client("client_id", "client_secret", base_url)
    requests_mock.post(client.oauth_url, json={"accessToken": "token"})
    yield client


class TestUpload(object):
    @pytest.mark.parametrize(
        "expected_media_type, path", [("image", "image.jpg"), ("movie", "movie.mp4")]
    )
    def test_ファイルをアップロードできること(
        self, mocker, requests_mock, client, expected_media_type, path
    ):
        expected_media_id = 1
        upload_url = "http://upload_url.example.com"

        file_mock = mocker.mock_open(read_data=b"image data")
        mocker.patch("pathlib.Path.open", file_mock)
        requests_mock.post(
            urljoin(client.api_url, f"{expected_media_type}s/"),
            json={"id": expected_media_id, "upload_url": upload_url},
        )
        requests_mock.put(upload_url)

        media_id, media_type = client.upload_to_s3(path)

        assert media_id == expected_media_id
        assert media_type == expected_media_type

    def test_正しい拡張子でない場合アップロードできないこと(self, client):
        path = "test.text"

        with pytest.raises(InvalidFileType):
            client.upload_to_s3(path)


class TestExtractKeypoint(object):
    def test_画像からキーポイント抽出ができること(self, requests_mock, client):
        keypoint_id = 1

        requests_mock.post(
            urljoin(client.api_url, "keypoints/"), json={"id": keypoint_id}
        )
        requests_mock.get(
            urljoin(client.api_url, f"keypoints/{keypoint_id}/"),
            json={"exec_status": "SUCCESS"},
        )

        result = client.extract_keypoint_from_image(1)

        assert result == keypoint_id

    def test_動画からキーポイント抽出ができること(self, requests_mock, client):
        keypoint_id = 1

        requests_mock.post(
            urljoin(client.api_url, "keypoints/"), json={"id": keypoint_id}
        )
        requests_mock.get(
            urljoin(client.api_url, f"keypoints/{keypoint_id}/"),
            json={"exec_status": "SUCCESS"},
        )

        result = client.extract_keypoint_from_movie(1)

        assert result == keypoint_id


def test_キーポイントデータを取得できること(requests_mock, client):
    keypoint_id = 1
    expected_keypoint = "[]"
    # expected_keypoint = '[{"0": [1, 2]}]'

    requests_mock.get(
        urljoin(client.api_url, f"keypoints/{keypoint_id}/"),
        json={"exec_status": "SUCCESS", "keypoint": expected_keypoint},
    )

    keypoint = client.get_keypoint(keypoint_id)

    assert keypoint == expected_keypoint


def test_解析結果を取得できること(requests_mock, client):
    analysis_id = 1
    expected_result = "[]"

    requests_mock.get(
        urljoin(client.api_url, f"analyses/{analysis_id}/"),
        json={"exec_status": "SUCCESS", "result": expected_result},
    )

    result = client.get_analysis(analysis_id)

    assert result == expected_result


def test_キーポイントを描画できること(requests_mock, client):
    keypoint_id = 1
    drawing_id = 1
    expected_drawing_url = "http://drawing_url.example.com"

    requests_mock.post(f"{client.api_url}drawings/", json={"id": drawing_id})
    requests_mock.get(
        f"{client.api_url}drawings/{drawing_id}/",
        json={"exec_status": "SUCCESS", "drawing_url": expected_drawing_url},
    )

    drawing_url = client.draw_keypoint(keypoint_id)

    assert drawing_url == expected_drawing_url


def test_キーポイントの解析ができること(requests_mock, client):
    keypoint_id = 1
    analysis_id = 1
    expected_result = "[]"

    requests_mock.post(f"{client.api_url}analyses/", json={"id": analysis_id})
    requests_mock.get(
        f"{client.api_url}analyses/{analysis_id}/",
        json={"exec_status": "SUCCESS", "result": expected_result},
    )

    result = client.analyze_keypoint(keypoint_id)

    assert result == expected_result


def test_ファイルをダウンロードできること(mocker, requests_mock, client, tmpdir):
    tmpdir = Path(tmpdir)
    url = "http://download.example.com/image.jpg"
    path = tmpdir / "image.jpg"

    requests_mock.get(url, content=b"image data")
    mkdir_mock = mocker.MagicMock()
    mocker.patch("pathlib.Path.mkdir", mkdir_mock)

    assert not path.exists()

    client.download(url, tmpdir)

    assert path.exists()
