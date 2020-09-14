import pytest

from anymotion_cli.commands.interactive import cli


@pytest.mark.parametrize(
    "args",
    [
        ["interactive"],
        ["interactive", "--profile", "test"],
    ],
)
def test_interactive(mocker, runner, args):
    repl_mock = mocker.MagicMock()
    mocker.patch("anymotion_cli.commands.interactive.repl", repl_mock)

    result = runner.invoke(cli, args, catch_exceptions=True)

    assert repl_mock.call_count == 1
    assert result.exit_code == 0
    assert result.output.startswith("Start interactive mode.")
