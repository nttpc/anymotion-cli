from textwrap import dedent

from encore_api_cli.core import cli


class TestAnalysis(object):
    def test_show(self, runner):
        result = runner.invoke(cli, ["analysis", "show", "444", "--only"])

        assert result.exit_code == 0
        assert result.output == dedent(
            """\

            [
              [
                {
                  "type": "angle",
                  "description": "leftShoulder, leftHip and leftKnee angles",
                  "values": [
                    120
                  ]
                }
              ]
            ]

            """
        )

    def test_list(self, runner):
        result = runner.invoke(cli, ["analysis", "list"])

        assert result.exit_code == 0
        assert result.output == dedent(
            """\

            [
              {
                "id": 444,
                "keypoint": 222,
                "execStatus": "SUCCESS"
              }
            ]

            """
        )


def test_analyze(runner):
    rule = (
        '[{"analysisType": "angle", "points": ["leftShoulder", "leftHip", "leftKnee"]}]'
    )
    result = runner.invoke(cli, ["analyze", "222", "--rule", rule])

    assert result.exit_code == 0
    assert result.output == dedent(
        f"""\
        Analysis started. (analysis id: 444)
        Success: Analysis is complete.
        """
    )


def test_download(tmp_path, runner):
    path = tmp_path / "image.jpg"

    assert not path.exists()

    result = runner.invoke(cli, ["download", "333", "-o", str(tmp_path)])

    assert result.exit_code == 0
    assert result.output == dedent(
        f"""\
        Downloaded the file to {path.resolve()}.
        """
    )
    assert path.exists()


def test_draw(tmp_path, runner):
    path = tmp_path / "image.jpg"

    assert not path.exists()

    result = runner.invoke(cli, ["draw", "222", "-o", str(tmp_path)])

    assert result.exit_code == 0
    assert result.output == dedent(
        f"""\
        Drawing started. (drawing id: 333)
        Success: Drawing is complete.
        Downloaded the file to {path.resolve()}.
        """
    )
    assert path.exists()


class TestDrawing(object):
    def test_show(self, runner):
        result = runner.invoke(cli, ["drawing", "show", "333"])

        assert result.exit_code == 0
        assert result.output == dedent(
            """\

            {
              "id": 333,
              "keypoint": 222,
              "drawingUrl": "http://s3.example.com/user/images/drawings/image.jpg",
              "execStatus": "SUCCESS",
              "failureDetail": null
            }

            """
        )

    def test_list(self, runner):
        result = runner.invoke(cli, ["drawing", "list"])

        assert result.exit_code == 0
        assert result.output == dedent(
            """\

            [
              {
                "id": 333,
                "keypoint": 222,
                "execStatus": "SUCCESS"
              }
            ]

            """
        )


def test_extract(runner):
    result = runner.invoke(cli, ["extract", "--image-id", "111"])

    assert result.exit_code == 0
    assert result.output == dedent(
        f"""\
        Keypoint extraction started. (keypoint id: 222)
        Success: Keypoint extraction is complete.
        """
    )


class TestImage(object):
    def test_show(self, runner):
        result = runner.invoke(cli, ["image", "show", "111"])

        assert result.exit_code == 0
        assert result.output == dedent(
            """\

            {
              "id": 111,
              "name": "image",
              "contentMd5": "contentmd5"
            }

            """
        )

    def test_list(self, runner):
        result = runner.invoke(cli, ["image", "list"])

        assert result.exit_code == 0
        assert result.output == dedent(
            """\

            [
              {
                "id": 111,
                "name": "image",
                "contentMd5": "contentmd5"
              }
            ]

            """
        )


class TestKeypoint(object):
    def test_show(self, runner):
        result = runner.invoke(cli, ["keypoint", "show", "222", "--only"])

        assert result.exit_code == 0
        assert result.output == dedent(
            """\

            [
              {
                "leftEye": [
                  12,
                  34
                ],
                "rightEye": [
                  34,
                  56
                ]
              }
            ]

            """
        )

    def test_list(self, runner):
        result = runner.invoke(cli, ["keypoint", "list"])

        assert result.exit_code == 0
        assert result.output == dedent(
            """\

            [
              {
                "id": 222,
                "image": 111,
                "movie": null,
                "execStatus": "SUCCESS"
              }
            ]

            """
        )


class TestMovie(object):
    def test_show(self, runner):
        result = runner.invoke(cli, ["movie", "show", "555"])

        assert result.exit_code == 0
        assert result.output == dedent(
            """\

            {
              "id": 555,
              "name": "movie",
              "contentMd5": "contentmd5"
            }

            """
        )

    def test_list(self, runner):
        result = runner.invoke(cli, ["movie", "list"])

        assert result.exit_code == 0
        assert result.output == dedent(
            """\

            [
              {
                "id": 555,
                "name": "movie",
                "contentMd5": "contentmd5"
              }
            ]

            """
        )


def test_upload(runner, image_path):
    result = runner.invoke(cli, ["upload", str(image_path)])

    assert result.exit_code == 0
    assert result.output == dedent(
        f"""\
        Success: Uploaded {image_path} to the cloud storage. (image id: 111)
        """
    )
