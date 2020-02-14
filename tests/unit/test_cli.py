import re

import pytest

from encore_api_cli.core import cli


@pytest.mark.parametrize("args", [None, ["--help"]])
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
        "keypoint",
        "movie",
        "upload",
    ],
)
def test_show_command_help_message(runner, command):
    result = runner.invoke(cli, [command, "--help"])

    assert result.exit_code == 0
    assert re.match(rf"^Usage: \w+ {command}", result.output)


def test_show_version(runner):
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert re.match(r"^\w+ version \d+.\d+.\d+([a|b|rc]\d+)?$", result.output)


def test_interactive(runner):
    result = runner.invoke(cli, ["--interactive"])

    assert result.exit_code == 0
    assert result.output.startswith("Start interactive mode.")
