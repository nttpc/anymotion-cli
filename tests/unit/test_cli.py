from click.testing import CliRunner

from encore_api_cli.cli import cli

import re
import pytest


@pytest.mark.parametrize(
    'command', ['analysis', 'configure', 'draw', 'image', 'keypoint', 'movie'])
def test_commands(command):
    runner = CliRunner()
    result = runner.invoke(cli, [command, '--help'])

    assert result.exit_code == 0
    assert re.match(rf'^Usage: \w+ {command}', result.output)


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])

    assert result.exit_code == 0
    assert re.match(r'^Usage:', result.output)


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])

    assert result.exit_code == 0
    assert re.match(r'^\w+, version \d+.\d+.\d+$', result.output)
