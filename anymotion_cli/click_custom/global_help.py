import click


class GlobalHelpOption(click.Option):
    """Inherited class to provide global option help."""

    def __init__(self, *args, **kwargs):
        is_global = kwargs.pop("is_global", False)
        if not isinstance(is_global, bool):
            raise
        self.is_global = is_global

        super().__init__(*args, **kwargs)


class GlobalHelpMixin(object):
    """Mixin class to provide global option help."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format_options(self, ctx, formatter):  # noqa: D102
        default_opts = []
        global_opts = []

        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                is_global = False
                if isinstance(param, GlobalHelpOption):
                    is_global = param.is_global
                if "--help" in rv[0]:
                    is_global = True

                if is_global:
                    global_opts.append(rv)
                else:
                    default_opts.append(rv)

        if default_opts:
            with formatter.section("Options"):
                formatter.write_dl(default_opts)
        if global_opts:
            with formatter.section("Global Options"):
                formatter.write_dl(global_opts)

        if isinstance(self, click.MultiCommand):
            self.format_commands(ctx, formatter)
