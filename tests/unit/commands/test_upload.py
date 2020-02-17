import pytest

from encore_api_cli.commands.upload import cli
from encore_sdk import FileTypeError, RequestsError


class TestUpload(object):
    def test_valid(self, runner, make_path, make_client_mock):
        path = make_path("image.jpg", is_file=True)
        expected = f"Success: Uploaded {path} to the cloud storage. (image id: 1)\n"
        client_mock = make_client_mock()

        result = runner.invoke(cli, ["upload", str(path)])

        assert result.exit_code == 0
        assert result.output == expected
        assert client_mock.call_count == 1

    def test_with_RequestsError(self, runner, make_path, make_client_mock):
        path = make_path("image.jpg", is_file=True)
        client_mock = make_client_mock(with_requests_error=True)

        result = runner.invoke(cli, ["upload", str(path)])

        assert result.exit_code == 1
        assert result.output == "Error: \n"
        assert client_mock.call_count == 1

    def test_with_FileTypeError(self, runner, make_path, make_client_mock):
        path = make_path("image.jpg", is_file=True)
        client_mock = make_client_mock(with_file_type_error=True)

        result = runner.invoke(cli, ["upload", str(path)])

        assert result.exit_code == 2
        assert result.output.endswith("Error: Invalid value: \n")
        assert client_mock.call_count == 1

    def test_invalid_params(self, runner, make_client_mock):
        client_mock = make_client_mock()

        result = runner.invoke(cli, ["upload"])

        assert result.exit_code == 2
        assert result.output.endswith('Error: Missing argument "PATH".\n')
        assert client_mock.call_count == 0

    @pytest.mark.parametrize(
        "file_name, is_file, is_dir, exists, expected",
        [
            (
                "image.jpg",
                True,
                False,
                False,
                'Error: Invalid value for "PATH": File "{}" does not exist.\n',
            ),
            (
                "dir",
                False,
                True,
                False,
                'Error: Invalid value for "PATH": File "{}" does not exist.\n',
            ),
            (
                "dir",
                False,
                True,
                True,
                'Error: Invalid value for "PATH": File "{}" is a directory.\n',
            ),
        ],
    )
    def test_invalid_path(
        self,
        runner,
        make_path,
        make_client_mock,
        file_name,
        is_file,
        is_dir,
        exists,
        expected,
    ):
        path = make_path(file_name, is_file=is_file, is_dir=is_dir, exists=exists)
        expected = expected.format(path)
        client_mock = make_client_mock()

        result = runner.invoke(cli, ["upload", str(path)])

        assert result.exit_code == 2
        assert result.output.endswith(expected)
        assert client_mock.call_count == 0

    @pytest.fixture
    def make_client_mock(self, mocker):
        def _make_client_mock(with_file_type_error=False, with_requests_error=False):
            client_mock = mocker.MagicMock()

            if with_file_type_error:
                client_mock.return_value.upload_to_s3.side_effect = FileTypeError()
            elif with_requests_error:
                client_mock.return_value.upload_to_s3.side_effect = RequestsError()
            else:
                client_mock.return_value.upload_to_s3.return_value = ("1", "image")

            mocker.patch("encore_api_cli.commands.upload.get_client", client_mock)

            return client_mock

        return _make_client_mock
