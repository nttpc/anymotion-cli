from textwrap import dedent

import pytest

from encore_api_cli.output import (
    echo,
    echo_json,
    echo_request,
    echo_response,
    echo_success,
)


@pytest.mark.parametrize(
    "is_show, expected",
    [("True", "message\n"), ("False", ""), (None, ""), ("invalid", "")],
)
def test_echo(capfd, monkeypatch, is_show, expected):
    monkeypatch.delenv("STDOUT_ISSHOW", raising=False)
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
    monkeypatch.delenv("STDOUT_ISSHOW", raising=False)
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
    "headers, json, expected",
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
        (None, None, "POST http://example.com\n\n"),
    ],
)
def test_echo_request(capfd, monkeypatch, headers, json, expected):
    monkeypatch.setenv("STDOUT_ISSHOW", "True")

    echo_request(
        "http://example.com", "POST", headers=headers, json=json,
    )

    out, err = capfd.readouterr()
    assert out == expected
    assert err == ""


@pytest.mark.parametrize(
    "status_code, reason, version, headers, json, expected",
    [
        (
            200,
            "OK",
            11,
            {"Content-Type": "application/json"},
            None,
            dedent(
                """\
                    HTTP/1.1 200 OK
                    Content-Type: application/json


                """
            ),
        ),
        (
            201,
            "Created",
            10,
            {"Content-Type": "application/json"},
            None,
            dedent(
                """\
                    HTTP/1.0 201 Created
                    Content-Type: application/json


                """
            ),
        ),
        (
            200,
            "OK",
            11,
            {"Content-Type": "application/json"},
            {"id": 1},
            dedent(
                """\
                    HTTP/1.1 200 OK
                    Content-Type: application/json

                    {
                      "id": 1
                    }



                """
            ),
        ),
    ],
)
def test_echo_response(
    capfd, monkeypatch, status_code, reason, version, headers, json, expected
):
    monkeypatch.setenv("STDOUT_ISSHOW", "True")

    echo_response(status_code, reason, version, headers, json)

    out, err = capfd.readouterr()
    assert out == expected
    assert err == ""
