"""Command Line Interface for AnyMotion API."""

import pkg_resources

from . import exceptions  # noqa: F401
from . import utils  # noqa: F401

__version__ = pkg_resources.get_distribution("encore_api_cli").version
