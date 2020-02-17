from textwrap import dedent

from encore_api_cli.core import cli


def test_upload(requests_mock, runner, image_path):
    upload_url = "http://s3.example.com/user/images/origins/image.jpg"
    requests_mock.post(
        "http://api.example.com/anymotion/v1/images/",
        json={"id": 1, "uploadUrl": upload_url},
    )
    requests_mock.put(upload_url)

    result = runner.invoke(cli, ["upload", str(image_path)])

    assert result.exit_code == 0
    assert result.output == dedent(
        f"""\
        Success: Uploaded {image_path} to the cloud storage. (image id: 1)
        """
    )
