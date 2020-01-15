from textwrap import dedent

import pytest

from encore_api_cli.output import echo, echo_http, echo_json, echo_success


@pytest.mark.parametrize(
    "is_show, expected",
    [("True", "message\n"), ("False", ""), (None, ""), ("invalid", "")],
)
def test_echo(capfd, monkeypatch, is_show, expected):
    if is_show:
        monkeypatch.setenv("STDOUT_ISSHOW", is_show)

    echo("message")

    out, err = capfd.readouterr()
    assert out == expected
    assert err == ""


@pytest.mark.parametrize(
    "is_show, expected",
    [("True", "Success: message\n"), ("False", ""), (None, ""), ("invalid", "")],
)
def test_echo_success(capfd, monkeypatch, is_show, expected):
    if is_show:
        monkeypatch.setenv("STDOUT_ISSHOW", is_show)

    echo_success("message")

    out, err = capfd.readouterr()
    assert out == expected
    assert err == ""


def test_echo_json(capfd):
    echo_json({"key": "value"})

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
def test_echo_http(capfd, monkeypatch, headers, data, expected):
    monkeypatch.setenv("STDOUT_ISSHOW", "True")

    echo_http(
        "http://example.com", "POST", headers=headers, data=data,
    )

    out, err = capfd.readouterr()
    assert out == expected
    assert err == ""
