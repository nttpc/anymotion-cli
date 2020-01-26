from pathlib import Path
from urllib.parse import urljoin

import pytest

from encore_api_cli.client import Client
from encore_api_cli.exceptions import InvalidFileType


@pytest.fixture
def client(requests_mock):
    base_url = "http://api.example.com/"
    client = Client("client_id", "client_secret", base_url, 5, 600)
    requests_mock.post(client._oauth_url, json={"accessToken": "token"})
    yield client


class TestGetData(object):
    def test_get_one_data(self, requests_mock, client):
        data = {"id": 1, "name": "image"}
        requests_mock.get(
            f"{client._api_url}images/1/", json=data,
        )
        result = client.get_one_data("images", 1)

        assert result == data

    def test_get_list_data(self, requests_mock, client):
        data = [{"id": 1, "name": "image"}, {"id": 2, "name": "image"}]
        requests_mock.get(
            f"{client._api_url}images/",
            json={"next": None, "previous": None, "maxPage": 1, "data": data},
        )
        result = client.get_list_data("images")

        assert result == data


class TestUpload(object):
    @pytest.mark.parametrize(
        "expected_media_type, path",
        [
            ("image", "image.jpg"),
            ("image", "image.JPG"),
            ("image", "image.jpeg"),
            ("image", "image.png"),
            ("movie", "movie.mp4"),
            ("movie", "movie.MP4"),
            ("movie", "movie.mov"),
        ],
    )
    def test_ファイルをアップロードできること(
        self, mocker, requests_mock, client, expected_media_type, path
    ):
        expected_media_id = 1
        upload_url = "http://upload_url.example.com"

        file_mock = mocker.mock_open(read_data=b"image data")
        mocker.patch("pathlib.Path.open", file_mock)
        requests_mock.post(
            urljoin(client._api_url, f"{expected_media_type}s/"),
            json={"id": expected_media_id, "uploadUrl": upload_url},
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
    def test_画像からキーポイント抽出を開始できること(self, requests_mock, client):
        image_id = 111
        expected_keypoint_id = 222
        requests_mock.post(
            urljoin(client._api_url, "keypoints/"), json={"id": expected_keypoint_id}
        )

        keypoint_id = client.extract_keypoint_from_image(image_id)

        assert keypoint_id == expected_keypoint_id

    def test_動画からキーポイント抽出を開始できること(self, requests_mock, client):
        movie_id = 111
        expected_keypoint_id = 222
        requests_mock.post(
            urljoin(client._api_url, "keypoints/"), json={"id": expected_keypoint_id}
        )

        keypoint_id = client.extract_keypoint_from_movie(movie_id)

        assert keypoint_id == expected_keypoint_id

    def test_キーポイント抽出を完了できること(self, requests_mock, client):
        keypoint_id = 1
        requests_mock.get(
            urljoin(client._api_url, f"keypoints/{keypoint_id}/"),
            json={"execStatus": "SUCCESS"},
        )

        status = client.wait_for_extraction(keypoint_id)

        assert status == "SUCCESS"


class TestDrawingKeypoint(object):
    def test_キーポイント描画を開始できること(self, requests_mock, client):
        keypoint_id = 1
        expected_drawing_id = 1
        requests_mock.post(
            f"{client._api_url}drawings/", json={"id": expected_drawing_id}
        )

        drawing_id = client.draw_keypoint(keypoint_id)

        assert drawing_id == expected_drawing_id

    def test_キーポイント描画を完了できること(self, requests_mock, client):
        drawing_id = 1
        expected_drawing_url = "http://drawing_url.example.com"
        requests_mock.get(
            f"{client._api_url}drawings/{drawing_id}/",
            json={"execStatus": "SUCCESS", "drawingUrl": expected_drawing_url},
        )

        status, drawing_url = client.wait_for_drawing(drawing_id)

        assert status == "SUCCESS"
        assert drawing_url == expected_drawing_url


class TestAnalysisKeypoint(object):
    def test_キーポイント解析を開始できること(self, requests_mock, client):
        keypoint_id = 111
        expected_analysis_id = 222
        requests_mock.post(
            f"{client._api_url}analyses/", json={"id": expected_analysis_id}
        )

        analysis_id = client.analyze_keypoint(keypoint_id)

        assert analysis_id == expected_analysis_id

    def test_キーポイント解析を完了できること(self, requests_mock, client):
        analysis_id = 222
        requests_mock.get(
            f"{client._api_url}analyses/{analysis_id}/",
            json={"execStatus": "SUCCESS", "result": "[]"},
        )

        status = client.wait_for_analysis(analysis_id)

        assert status == "SUCCESS"


def test_ファイルをダウンロードできること(mocker, requests_mock, client, tmpdir):
    url = "http://download.example.com/image.jpg"
    path = Path(tmpdir) / "image.jpg"

    requests_mock.get(url, content=b"image data")
    mocker.patch("pathlib.Path.mkdir", mocker.MagicMock())

    assert not path.exists()

    client.download(url, path)

    assert path.exists()
