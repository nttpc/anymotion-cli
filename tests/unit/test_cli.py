import re

import pytest
from click.testing import CliRunner

from encore_api_cli.cli import cli


@pytest.mark.parametrize(
    "command",
    [
        "analysis",
        "analyze",
        "configure",
        "draw",
        "image",
        "keypoint",
        "movie",
        "upload",
    ],
)
def test_コマンドが実行できること(command):
    runner = CliRunner()
    result = runner.invoke(cli, [command, "--help"])

    assert result.exit_code == 0
    assert re.match(rf"^Usage: \w+ {command}", result.output)


def test_helpが表示されること():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert re.match(r"^Usage:", result.output)


def test_versionが表示されること():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert re.match(r"^\w+, version \d+.\d+.\d+$", result.output)
