from textwrap import dedent

import pytest

from encore_api_cli.output import write_http
from encore_api_cli.output import write_json_data
from encore_api_cli.output import write_message
from encore_api_cli.output import write_success


@pytest.mark.parametrize("stdout_isatty, expected", [(True, "message\n"), (False, "")])
def test_write_message(capfd, stdout_isatty, expected):
    write_message("message", stdout_isatty=stdout_isatty)

    out, err = capfd.readouterr()
    assert out == expected
    assert err == ""


@pytest.mark.parametrize(
    "stdout_isatty, expected", [(True, "Success: message\n"), (False, "")]
)
def test_write_success(capfd, stdout_isatty, expected):
    write_success("message", stdout_isatty=stdout_isatty)

    out, err = capfd.readouterr()
    assert out == expected
    assert err == ""


def test_write_json_data(capfd):
    write_json_data({"key": "value"})

    out, err = capfd.readouterr()
    assert out == dedent(
        """\
            {
              "key": "value"
            }

        """
    )
    assert err == ""


@pytest.mark.parametrize(
    "headers, data, expected",
    [
        (
            {"Content-Type": "application/json"},
            {"key": "value"},
            dedent(
                """\
                    POST http://example.com
                    Content-Type: application/json

                    {
                      "key": "value"
                    }

                """
            ),
        ),
        (
            None,
            {"key": "value"},
            dedent(
                """\
                    POST http://example.com

                    {
                      "key": "value"
                    }

                """
            ),
        ),
        (None, None, "POST http://example.com\n"),
    ],
)
def test_write_http(capfd, headers, data, expected):
    write_http(
        "http://example.com", "POST", headers=headers, data=data, stdout_isatty=True,
    )

    out, err = capfd.readouterr()
    assert out == expected
    assert err == ""
