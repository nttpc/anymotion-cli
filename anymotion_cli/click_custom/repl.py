# Copyright (c) 2020 NTTPC Communications, Inc.
# See https://github.com/nttpc/anymotion-cli/blob/master/LICENSE.

# Classes under this library were originally taken from click-repl,
# Copyright (c) 2014-2015 Markus Unterwaditzer & contributors.
# These Classes are licensed under the MIT license.
# See https://github.com/click-contrib/click-repl/blob/master/LICENSE.


import os
import shlex
import sys
from collections import defaultdict

import click
import click._bashcomplete
import click.parser
from click.exceptions import Exit as ClickExit
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.shortcuts import prompt

from ..exceptions import ExitReplException

_internal_commands = dict()
_disable_options = ("--interactive", "--profile")


def _register_internal_command(names, target, description=None):
    if not callable(target):
        raise ValueError("Internal command must be a callable")

    if isinstance(names, str):
        names = [names]
    elif not isinstance(names, (list, tuple)):
        raise ValueError('"names" must be a string or a list / tuple')

    for name in names:
        _internal_commands[name] = (target, description)


def _get_registered_target(name, default=None):
    target_info = _internal_commands.get(name)
    if target_info:
        return target_info[0]
    return default


def _exit_internal():
    raise ExitReplException()


def _help_internal():
    formatter = click.HelpFormatter()
    formatter.write_heading("Usage in interactive mode")
    formatter.indent()
    with formatter.section("External Commands"):
        formatter.write_text('prefix external commands with "!"')
    with formatter.section("Internal Commands"):
        formatter.write_text('prefix internal commands with ":"')
        info_table = defaultdict(list)
        for mnemonic, target_info in _internal_commands.items():
            info_table[target_info[1]].append(mnemonic)
        formatter.write_dl(
            (
                click.style(
                    ", ".join((f":{mnemonic}" for mnemonic in sorted(mnemonics))),
                    fg="cyan",
                ),
                description,
            )
            for description, mnemonics in info_table.items()
        )
    return formatter.getvalue()


_register_internal_command(["exit"], _exit_internal, "Exits the interactive mode.")
_register_internal_command(["help"], _help_internal, "Show this message.")


class ClickCompleter(Completer):
    """Click completer."""

    def __init__(self, cli):
        self.cli = cli

    def get_completions(self, document, complete_event=None):
        """Code analogous to click._bashcomplete.do_complete."""
        try:
            args = shlex.split(document.text_before_cursor)
        except ValueError:
            # Invalid command, perhaps caused by missing closing quotation.
            return

        cursor_within_command = (
            document.text_before_cursor.rstrip() == document.text_before_cursor
        )

        if args and cursor_within_command:
            # We've entered some text and no space, give completions for the
            # current word.
            incomplete = args.pop()
        else:
            # We've not entered anything, either at all or for the current
            # command, so give all relevant completions for this context.
            incomplete = ""

        ctx = click._bashcomplete.resolve_ctx(self.cli, "", args)
        if ctx is None:
            return

        choices = []
        for param in ctx.command.params:
            if isinstance(param, click.Option):
                for options in (param.opts, param.secondary_opts):
                    for o in options:
                        if o in _disable_options:
                            continue
                        choices.append(
                            Completion(
                                str(o), -len(incomplete), display_meta=param.help
                            )
                        )
            elif isinstance(param, click.Argument):
                if isinstance(param.type, click.Choice):
                    for choice in param.type.choices:
                        choices.append(Completion(str(choice), -len(incomplete)))

        if isinstance(ctx.command, click.MultiCommand):
            for name in ctx.command.list_commands(ctx):
                command = ctx.command.get_command(ctx, name)
                choices.append(
                    Completion(
                        str(name),
                        -len(incomplete),
                        display_meta=command.short_help,
                    )
                )

        for item in choices:
            if item.text.startswith(incomplete):
                yield item


def bootstrap_prompt(prompt_kwargs, group):
    """Bootstrap prompt_toolkit kwargs or use user defined values.

    :param prompt_kwargs: The user specified prompt kwargs.
    """
    prompt_kwargs = prompt_kwargs or {}

    defaults = {
        "history": InMemoryHistory(),
        "completer": ClickCompleter(group),
        "message": "> ",
    }

    for key in defaults:
        default_value = defaults[key]
        if key not in prompt_kwargs:
            prompt_kwargs[key] = default_value

    return prompt_kwargs


def repl(
    old_ctx,
    prompt_kwargs=None,
    allow_system_commands=True,
    allow_internal_commands=True,
):
    """Start an interactive shell.

    All subcommands are available in it.

    :param old_ctx: The current Click context.
    :param prompt_kwargs: Parameters passed to
        :py:func:`prompt_toolkit.shortcuts.prompt`.
    If stdin is not a TTY, no prompt will be printed, but only commands read
    from stdin.
    """
    # parent should be available, but we're not going to bother if not
    group_ctx = old_ctx.parent or old_ctx
    group = group_ctx.command
    isatty = sys.stdin.isatty()

    # Delete the REPL command from those available, as we don't want to allow
    # nesting REPLs (note: pass `None` to `pop` as we don't want to error if
    # REPL command already not present for some reason).
    repl_command_name = old_ctx.command.name
    if isinstance(group_ctx.command, click.CommandCollection):
        available_commands = {
            cmd_name: cmd_obj
            for source in group_ctx.command.sources
            for cmd_name, cmd_obj in source.commands.items()
        }
    else:
        available_commands = group_ctx.command.commands
    available_commands.pop(repl_command_name, None)

    prompt_kwargs = bootstrap_prompt(prompt_kwargs, group)

    if isatty:

        def get_command():
            return prompt(**prompt_kwargs)

    else:
        get_command = sys.stdin.readline

    while True:
        try:
            command = get_command()
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

        if not command:
            if isatty:
                continue
            else:
                break

        if allow_system_commands and dispatch_repl_commands(command):
            continue

        if allow_internal_commands:
            try:
                result = handle_internal_commands(command)
                if isinstance(result, str):
                    click.echo(result)
                    continue
            except ExitReplException:
                break

        try:
            args = shlex.split(command)
        except ValueError as e:
            click.echo("{}: {}".format(type(e).__name__, e))
            continue

        def check_option(args):
            for arg in args:
                if arg in _disable_options:
                    click.echo(f"Error: unavailable option in interactive mode: {arg}")
                    return False
            return True

        if not check_option(args):
            continue

        try:
            with group.make_context(None, args, parent=group_ctx) as ctx:
                group.invoke(ctx)
                ctx.exit()
        except click.ClickException as e:
            e.show()
        except ClickExit:
            pass
        except SystemExit:
            pass
        except ExitReplException:
            break


def dispatch_repl_commands(command):
    """Execute system commands entered in the repl.

    System commands are all commands starting with "!".
    """
    if command.startswith("!"):
        os.system(command[1:])  # nosec
        return True

    return False


def handle_internal_commands(command):
    """Run repl-internal commands.

    Repl-internal commands are all commands starting with ":".
    """
    if command.startswith(":"):
        target = _get_registered_target(command[1:], default=None)
        if target:
            return target()
