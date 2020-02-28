from textwrap import dedent

import pytest
from click.testing import CliRunner


@pytest.fixture(autouse=True)
def configure(monkeypatch, tmp_path):
    (tmp_path / ".anymotion").mkdir()
    (tmp_path / ".anymotion" / "config").write_text(
        dedent(
            """\
            [default]
            anymotion_api_url = http://api.example.com/anymotion/v1/
            """
        )
    )
    (tmp_path / ".anymotion" / "credentials").write_text(
        dedent(
            """\
            [default]
            anymotion_client_secret = client_secret
            anymotion_client_id = client_id
            """
        )
    )

    monkeypatch.setenv("ANYMOTION_ROOT", str(tmp_path))
    monkeypatch.delenv("ANYMOTION_API_URL", raising=False)
    monkeypatch.delenv("ANYMOTION_CLIENT_ID", raising=False)
    monkeypatch.delenv("ANYMOTION_CLIENT_SECRET", raising=False)
    monkeypatch.setenv("ANYMOTION_USE_SPINNER", "false")
    monkeypatch.setenv("ANYMOTION_STDOUT_ISSHOW", "true")


@pytest.fixture(autouse=True)
def set_requests_mock(requests_mock):
    oauth_url = "http://api.example.com/v1/oauth/accesstokens"
    requests_mock.post(oauth_url, json={"accessToken": "token"})


@pytest.fixture
def runner():
    yield CliRunner()


@pytest.fixture
def image_path(tmp_path):
    path = tmp_path / "image.jpg"
    path.touch()
    yield path


@pytest.fixture(autouse=True)
def api_requests_mock(requests_mock):
    """Set api response mock.

    data
        image_id = 111
        keypoint_id = 222
        drawing_id = 333
        analysis_id = 444

        movie_id = 555
    """
    api_url = "http://api.example.com/anymotion/v1/"

    # GET images
    requests_mock.get(
        f"{api_url}images/",
        json={
            "next": None,
            "previous": None,
            "maxPage": 1,
            "data": [{"id": 111, "name": "image", "contentMd5": "contentmd5"}],
        },
    )

    requests_mock.get(
        f"{api_url}images/111/",
        json={"id": 111, "name": "image", "contentMd5": "contentmd5"},
    )

    # POST images
    requests_mock.post(
        f"{api_url}images/",
        json={
            "id": 111,
            "uploadUrl": "http://s3.example.com/user/images/origins/image.jpg",
        },
    )

    # GET movies
    requests_mock.get(
        f"{api_url}movies/",
        json={
            "next": None,
            "previous": None,
            "maxPage": 1,
            "data": [{"id": 555, "name": "movie", "contentMd5": "contentmd5"}],
        },
    )

    requests_mock.get(
        f"{api_url}movies/555/",
        json={"id": 555, "name": "movie", "contentMd5": "contentmd5"},
    )

    # GET keypoints
    requests_mock.get(
        f"{api_url}keypoints/",
        json={
            "next": None,
            "previous": None,
            "maxPage": 1,
            "data": [{"id": 222, "image": 111, "movie": None, "execStatus": "SUCCESS"}],
        },
    )

    requests_mock.get(
        f"{api_url}keypoints/222/",
        json={
            "id": 222,
            "image": 111,
            "movie": None,
            "keypoint": [{"leftEye": [12, 34], "rightEye": [34, 56]}],
            "execStatus": "SUCCESS",
            "failureDetail": None,
        },
    )

    # POST keypoints
    requests_mock.post(
        f"{api_url}keypoints/", json={"id": 222},
    )

    # GET drawings
    requests_mock.get(
        f"{api_url}drawings/",
        json={
            "next": None,
            "previous": None,
            "maxPage": 1,
            "data": [{"id": 333, "keypoint": 222, "execStatus": "SUCCESS"}],
        },
    )

    requests_mock.get(
        f"{api_url}drawings/333/",
        json={
            "id": 333,
            "keypoint": 222,
            "drawingUrl": "http://s3.example.com/user/images/drawings/image.jpg",
            "execStatus": "SUCCESS",
            "failureDetail": None,
        },
    )

    # POST drawings
    requests_mock.post(
        f"{api_url}drawings/", json={"id": 333},
    )

    # GET analyses
    requests_mock.get(
        f"{api_url}analyses/",
        json={
            "next": None,
            "previous": None,
            "maxPage": 1,
            "data": [{"id": 444, "keypoint": 222, "execStatus": "SUCCESS"}],
        },
    )

    requests_mock.get(
        f"{api_url}analyses/444/",
        json={
            "id": 444,
            "keypoint": 222,
            "execStatus": "SUCCESS",
            "result": [
                [
                    {
                        "type": "angle",
                        "description": "leftShoulder, leftHip and leftKnee angles",
                        "values": [120],
                    }
                ]
            ],
        },
    )

    # POST analyses
    requests_mock.post(
        f"{api_url}analyses/", json={"id": 444},
    )

    # GET S3
    requests_mock.get(
        "http://s3.example.com/user/images/drawings/image.jpg", content=b"dummy data",
    )

    # PUT S3
    requests_mock.put("http://s3.example.com/user/images/origins/image.jpg")
