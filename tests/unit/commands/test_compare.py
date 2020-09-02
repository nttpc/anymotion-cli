from textwrap import dedent

import pytest
from anymotion_sdk import RequestsError

from anymotion_cli.commands.compare import cli


class TestCompare(object):
    @pytest.mark.parametrize(
        "status, expected, exit_code",
        [
            ("SUCCESS", "Success: Comparison is complete.", 0),
            ("TIMEOUT", "Error: Comparison is timed out.", 1),
            ("FAILURE", "Error: Comparison failed.\nmessage", 1),
        ],
    )
    def test_valid(self, runner, make_client, status, expected, exit_code):
        comparison_id = 333
        client_mock = make_client(status=status, comparison_id=comparison_id)

        result = runner.invoke(cli, ["compare", "111", "222"])

        assert client_mock.call_count == 1
        assert result.exit_code == exit_code
        assert result.output == dedent(
            f"Comparison started. (comparison id: {comparison_id})\n{expected}\n"
        )

    def test_with_spinner(self, monkeypatch, runner, make_client):
        monkeypatch.setenv("ANYMOTION_USE_SPINNER", "true")
        client_mock = make_client()

        result = runner.invoke(cli, ["compare", "111", "222"])

        assert client_mock.call_count == 1
        assert result.exit_code == 0
        assert "Processing..." in result.output

    @pytest.mark.parametrize(
        "with_compare_exception, with_wait_exception", [(True, True), (False, True)]
    )
    def test_with_requests_error(
        self, runner, make_client, with_compare_exception, with_wait_exception
    ):
        client_mock = make_client(
            with_compare_exception=with_compare_exception,
            with_wait_exception=with_wait_exception,
        )
        result = runner.invoke(cli, ["compare", "111", "222"])

        assert client_mock.call_count == 1
        assert result.exit_code == 1
        assert result.output.endswith("Error: requests error\n")

    @pytest.mark.parametrize(
        "args, expected",
        [
            (["compare"], "Error: Missing argument 'SOURCE_ID'.\n",),
            (["compare", "111"], "Error: Missing argument 'TARGET_ID'.\n",),
        ],
    )
    def test_invalid_params(self, runner, make_client, args, expected):
        client_mock = make_client()
        result = runner.invoke(cli, args)

        assert client_mock.call_count == 0
        assert result.exit_code == 2
        assert result.output.endswith(expected)

    @pytest.fixture
    def make_client(self, mocker):
        def _make_client(
            status="SUCCESS",
            comparison_id=111,
            with_compare_exception=False,
            with_wait_exception=False,
        ):
            client_mock = mocker.MagicMock()

            compare_mock = client_mock.return_value.compare_keypoint
            if with_compare_exception:
                compare_mock.side_effect = RequestsError("requests error")
            else:
                compare_mock.return_value = comparison_id

            wait_mock = client_mock.return_value.wait_for_comparison
            if with_wait_exception:
                wait_mock.side_effect = RequestsError("requests error")
            else:
                wait_mock.return_value.status = status
                if status == "FAILURE":
                    wait_mock.return_value.failure_detail = "message"

            mocker.patch("anymotion_cli.commands.compare.get_client", client_mock)
            return client_mock

        return _make_client
