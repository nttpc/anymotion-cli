import os
from configparser import ConfigParser, SectionProxy
from distutils.util import strtobool
from pathlib import Path
from typing import Any, Optional, Tuple, Union

from .config import (
    API_URL,
    IS_DOWNLOAD,
    IS_OPEN,
    POLLING_INTERVAL,
    TIMEOUT,
    get_app_dir,
)
from .exceptions import SettingsValueError


class Settings(object):
    """Read and write settings.

    Attributes:
        is_ok (bool): Whether credentials are valid value.
        client_id (Optional[str]): The value used for authentication.
        client_secret (Optional[str]): The value used for authentication.
        api_url (str): The AnyMotion API URL to request.
        interval (int): The interval time(sec).
        timeout (int): The timeout period(sec).

    Note:
        interval and timeout is used only when requesting asynchronous processing.
    """

    def __init__(self, profile_name: str, use_env: bool = True):
        settings_dir = get_app_dir()
        config_file = settings_dir / "config"
        credentials_file = settings_dir / "credentials"

        self._config = _Profile(config_file, profile_name)
        self._credentials = _Profile(credentials_file, profile_name)

        self._env = _Environment(use_env)

    @property
    def is_ok(self) -> bool:
        """Whether credentials are valid value."""
        return self.client_id is not None and self.client_secret is not None

    @property
    def client_id(self) -> Optional[str]:
        """Return the value used for authentication."""
        value_from_env = self._env.anymotion_client_id
        value_from_file = self._credentials.anymotion_client_id
        return value_from_env or value_from_file

    @property
    def client_secret(self) -> Optional[str]:
        """Return the value used for authentication."""
        value_from_env = self._env.anymotion_client_secret
        value_from_file = self._credentials.anymotion_client_secret
        return value_from_env or value_from_file

    @property
    def api_url(self) -> str:
        """Return the AnyMotion API URL to request.

        If not in config file, return the default value.
        """
        # TODO: use env
        # value_from_env = self._env.anymotion_api_url
        # value_from_file = self._config.anymotion_api_url
        # return value_from_env or value_from_file or API_URL
        return self._config.anymotion_api_url or API_URL

    @property
    def interval(self) -> int:
        """Return the interval time(sec).

        If not in config file, return the default value.

        Raises:
            SettingsValueError
        """
        interval = self._config.polling_interval or POLLING_INTERVAL
        return self._to_int_with_check(interval, "polling_interval", 1)

    @property
    def timeout(self) -> int:
        """Return the timeout period(sec).

        If not in config file, return the default value.

        Raises:
            SettingsValueError
        """
        timeout = self._config.timeout or TIMEOUT
        return self._to_int_with_check(timeout, "timeout", 1)

    @property
    def is_download(self) -> Optional[bool]:
        """Return default download flag."""
        is_download = self._config.is_download or IS_DOWNLOAD
        return self._to_optional_bool_with_check(is_download, "is_download")

    @property
    def is_open(self) -> Optional[bool]:
        """Return default open flag."""
        is_open = self._config.is_open or IS_OPEN
        return self._to_optional_bool_with_check(is_open, "is_open")

    def write_config(self, api_url: str) -> None:
        """Update config file.

        Update only when different from current value.

        Raises:
            SettingsValueError
        """
        if api_url == self.api_url:
            return
        if api_url is None or "anymotion" not in api_url:
            raise SettingsValueError("api_url is invald.")

        self._config.anymotion_api_url = api_url
        self._config.save()

    def write_credentials(self, client_id: str, client_secret: str) -> None:
        """Update credentials file.

        Raises:
            SettingsValueError
        """
        if client_id is None or client_secret is None:
            raise SettingsValueError("client_id or client_secret is invald.")

        self._credentials.anymotion_client_id = client_id
        self._credentials.anymotion_client_secret = client_secret
        self._credentials.save()

    def _to_int_with_check(
        self, value: Union[str, int], name: str, min_value: int
    ) -> int:
        """Convert value to int.

        Returns:
            The converted value.

        Raises:
            SettingsValueError: If conversion is not possible or value is less
            than min_value.
        """
        try:
            x = int(value)
        except ValueError:
            message = f"The {name} value is invalid: {value}"
            raise SettingsValueError(message)
        if x < min_value:
            th = min_value - 1
            message = f"The {name} value must be greater than {th}: {x}"
            raise SettingsValueError(message)
        return x

    def _to_optional_bool_with_check(
        self, value: Optional[Union[bool, str]], name: str
    ) -> Optional[bool]:
        if value is None or isinstance(value, bool):
            return value
        elif isinstance(value, str):
            try:
                value = bool(strtobool(value))
            except ValueError:
                message = f"The {name} value is invalid: {value}"
                raise SettingsValueError(message)
            return value
        else:
            raise Exception(f"The {name} value is invalid: {value}")


class _Profile(object):
    def __init__(self, file: Path, profile_name: str):
        self._file = file
        self._parser, self._section = self._read(file, profile_name)

    def __getattr__(self, name: str) -> Optional[str]:
        return self._section.get(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name[0] == "_":
            object.__setattr__(self, name, value)
        else:
            self._section[name] = value

    def save(self) -> None:
        """Save profile to file."""
        with self._file.open("w") as f:
            self._parser.write(f)

    def _read(self, file: Path, profile_name: str) -> Tuple[ConfigParser, SectionProxy]:
        parser = ConfigParser()
        if file.exists():
            parser.read(file)

        try:
            section = parser[profile_name]
        except KeyError:
            parser[profile_name] = {}
            section = parser[profile_name]

        return parser, section


class _Environment(object):
    def __init__(self, use_env: bool):
        self._use_env = use_env

    def __getattr__(self, name: str) -> Optional[str]:
        if self._use_env:
            return os.getenv(name.upper())
        else:
            return None
