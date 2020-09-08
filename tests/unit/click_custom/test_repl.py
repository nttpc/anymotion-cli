import io

import click
from prompt_toolkit.document import Document

from anymotion_cli.click_custom.repl import ClickCompleter, repl


class TestCompletion(object):
    def test_basic(self):
        @click.group()
        def root_command():
            pass

        @root_command.group()
        def first_level_command():
            pass

        @first_level_command.command()
        def second_level_command_one():
            pass

        @first_level_command.command()
        def second_level_command_two():
            pass

        c = ClickCompleter(root_command)
        completions = list(c.get_completions(Document("first-level-command ")))

        assert set(x.text for x in completions) == set(
            ["second-level-command-one", "second-level-command-two"]
        )

    def test_argument(self):
        @click.group()
        def root_command():
            pass

        @root_command.command()
        @click.argument("handler", type=click.Choice(["foo", "bar"]))
        def arg_cmd():
            pass

        c = ClickCompleter(root_command)
        completions = list(c.get_completions(Document("arg-cmd ")))

        assert set(x.text for x in completions) == set(["foo", "bar"])

    def test_option(self):
        @click.group()
        def root_command():
            pass

        @root_command.command()
        @click.option("--foo")
        @click.option("--bar")
        @click.option("--interactive")
        def cmd():
            pass

        c = ClickCompleter(root_command)
        completions = list(c.get_completions(Document("cmd ")))

        assert set(x.text for x in completions) == set(["--foo", "--bar"])

    def test_command_collection(self):
        @click.group()
        def foo_group():
            pass

        @foo_group.command()
        def foo_cmd():
            pass

        @click.group()
        def foobar_group():
            pass

        @foobar_group.command()
        def foobar_cmd():
            pass

        c = ClickCompleter(click.CommandCollection(sources=[foo_group, foobar_group]))
        completions = list(c.get_completions(Document("foo")))

        assert set(x.text for x in completions) == set(["foo-cmd", "foobar-cmd"])


class TestRepl(object):
    def test_exit(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO(":exit"))

        @click.group()
        def root_command():
            pass

        ctx = root_command.make_context("cli", [""])
        repl(ctx)

    def test_show_help(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO(":help"))

        @click.group()
        def root_command():
            pass

        ctx = root_command.make_context("cli", [""])
        repl(ctx)

    def test_run_external_cmd(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("!ls"))

        @click.group()
        def root_command():
            pass

        ctx = root_command.make_context("cli", [""])
        repl(ctx)

    def test_run_cmd(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("cmd"))

        @click.group()
        def root_command():
            pass

        @root_command.command()
        def cmd():
            pass

        ctx = root_command.make_context("cli", [""])
        repl(ctx)

    def test_run_disable_option(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("cmd --interactive"))

        @click.group()
        def root_command():
            pass

        @root_command.command()
        @click.option("--interactive")
        def cmd():
            pass

        ctx = root_command.make_context("cli", [""])
        repl(ctx)

    def test_run_error_cmd(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("no-cmd"))

        @click.group()
        def root_command():
            pass

        ctx = root_command.make_context("cli", [""])
        repl(ctx)
