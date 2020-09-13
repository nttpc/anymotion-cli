import inspect

from click.decorators import _param_memo  # type: ignore

from .core import CustomOption


def custom_option(*param_decls, **attrs):
    """Attaches custom option to the command."""

    def decorator(f):
        option_attrs = attrs.copy()

        if "help" in option_attrs:
            option_attrs["help"] = inspect.cleandoc(option_attrs["help"])
        OptionClass = option_attrs.pop("cls", CustomOption)
        _param_memo(f, OptionClass(param_decls, **option_attrs))
        return f

    return decorator
