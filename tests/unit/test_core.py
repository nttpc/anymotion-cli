import re

import pytest

from anymotion_cli.core import cli


@pytest.mark.parametrize("args", [None, ["-h"], ["--help"]])
def test_show_help_message(runner, args):
    result = runner.invoke(cli, args)

    assert result.exit_code == 0
    assert re.match(r"^Usage:", result.output)


@pytest.mark.parametrize(
    "command",
    [
        "analysis",
        "analyze",
        "configure",
        "download",
        "draw",
        "drawing",
        "extract",
        "image",
        "interactive",
        "keypoint",
        "movie",
        "upload",
    ],
)
@pytest.mark.parametrize("option", ["-h", "--help"])
def test_show_command_help_message(runner, command, option):
    result = runner.invoke(cli, [command, option])

    assert result.exit_code == 0
    assert re.match(rf"^Usage: \w+ {command}", result.output)


@pytest.mark.parametrize(
    "args",
    [
        ["-V"],
        ["--version"],
    ],
)
def test_show_version(runner, args):
    result = runner.invoke(cli, args)

    assert result.exit_code == 0
    assert re.match(
        r"^\w+ version \d+\.\d+(\.\d+)?((a|b|rc|\.dev)\d+)?$", result.output
    )


def test_show_more_version(runner):
    pattern = r"\d+\.\d+(\.\d+)?((a|b|rc|\.dev)\d+)?"
    result = runner.invoke(cli, ["-VV"])

    assert result.exit_code == 0
    assert re.match(
        fr"^\w+ version {pattern} \(anymotion-sdk {pattern}, Python {pattern}\)$",
        result.output,
    )


@pytest.mark.parametrize(
    "args",
    [
        ["--interactive"],
        ["--interactive", "--profile", "test"],
    ],
)
def test_interactive(runner, args):
    result = runner.invoke(cli, args)

    assert result.exit_code == 0
    assert "Start interactive mode." in result.output
