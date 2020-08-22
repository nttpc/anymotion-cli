from textwrap import dedent

import pytest

from anymotion_cli.output import (
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
    monkeypatch.delenv("ANYMOTION_STDOUT_ISSHOW", raising=False)
    if is_show:
        monkeypatch.setenv("ANYMOTION_STDOUT_ISSHOW", is_show)

    echo("message")

    out, err = capfd.readouterr()
    assert out == expected
    assert err == ""


@pytest.mark.parametrize(
    "is_show, expected",
    [("True", "Success: message\n"), ("False", ""), (None, ""), ("invalid", "")],
)
def test_echo_success(capfd, monkeypatch, is_show, expected):
    monkeypatch.delenv("ANYMOTION_STDOUT_ISSHOW", raising=False)
    if is_show:
        monkeypatch.setenv("ANYMOTION_STDOUT_ISSHOW", is_show)

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
def test_echo_request(mocker, capfd, monkeypatch, headers, json, expected):
    monkeypatch.setenv("ANYMOTION_STDOUT_ISSHOW", "True")

    request_mock = mocker.MagicMock()
    request_mock.return_value.prepare.return_value.url = "http://example.com"
    request_mock.return_value.method = "POST"
    request_mock.return_value.headers = headers
    request_mock.return_value.json = json

    echo_request(request_mock())

    out, err = capfd.readouterr()
    assert out == expected
    assert err == ""


@pytest.mark.parametrize(
    "status_code, reason, version, headers, content, expected",
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
            b'{"id": 1}',
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
        (
            200,
            "OK",
            11,
            None,
            None,
            dedent(
                """\
                    HTTP/1.1 200 OK


                """
            ),
        ),
        (
            200,
            "OK",
            11,
            {"Content-Type": "text/plain"},
            b"message",
            dedent(
                """\
                    HTTP/1.1 200 OK
                    Content-Type: text/plain

                    message


                """
            ),
        ),
        (
            200,
            "OK",
            11,
            None,
            b"\0",
            dedent(
                """\
                    HTTP/1.1 200 OK

                    NOTE: binary data not shown


                """
            ),
        ),
    ],
)
def test_echo_response(
    mocker,
    capfd,
    monkeypatch,
    status_code,
    reason,
    version,
    headers,
    content,
    expected,
):
    monkeypatch.setenv("ANYMOTION_STDOUT_ISSHOW", "True")

    response_mock = mocker.MagicMock()
    response_mock.return_value.status_code = status_code
    response_mock.return_value.reason = reason
    response_mock.return_value.raw.version = version
    response_mock.return_value.headers = headers
    response_mock.return_value.content = content

    echo_response(response_mock())

    out, err = capfd.readouterr()
    assert out == expected
    assert err == ""
