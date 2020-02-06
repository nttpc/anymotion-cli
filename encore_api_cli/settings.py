import os
from configparser import ConfigParser, SectionProxy
from pathlib import Path
from typing import Any, Optional, Tuple, Union

from .exceptions import SettingsValueError

# default values
API_URL = "https://api.customer.jp/anymotion/v1/"
POLLING_INTERVAL = 5
TIMEOUT = 600


class Settings(object):
    """Read and write settings.

    Attributes:
        client_id (Optional[str]): The value used for authentication.
        client_secret (Optional[str]): The value used for authentication.
        api_url (str): The AnyMotion API URL to request.
        interval (int): The interval time(sec).
        timeout (int): The timeout period(sec).

    Note:
        interval and timeout is used only when requesting asynchronous processing.
    """

    def __init__(self, profile_name: str, use_env: bool = True):
        settings_dir = Path(os.getenv("ANYMOTION_ROOT", Path.home())) / ".anymotion"
        settings_dir.mkdir(exist_ok=True)

        config_file = settings_dir / "config"
        credentials_file = settings_dir / "credentials"

        self._config = Profile(config_file, profile_name)
        self._credentials = Profile(credentials_file, profile_name)

        self._env = Environment(use_env)

    def is_ok(self) -> bool:
        """Whether credentials are valid value."""
        return self.client_id is not None and self.client_secret is not None

    def write_config(self, api_url: str) -> None:
        """Update config file.

        Update only when different from current value.
        """
        if api_url == self.api_url:
            return
        if api_url is None or "anymotion" not in api_url:
            raise ValueError("api_url is invald.")

        self._config.anymotion_api_url = api_url
        self._config.save()

    def write_credentials(self, client_id: str, client_secret: str) -> None:
        """Update credentials file."""
        if client_id is None or client_secret is None:
            raise ValueError("client_id or client_secret is invald.")

        self._credentials.anymotion_client_id = client_id
        self._credentials.anymotion_client_secret = client_secret
        self._credentials.save()

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
        return self._config.anymotion_api_url or API_URL

    @property
    def interval(self) -> int:
        """Return the interval time(sec).

        If not in config file, return the default value.
        """
        interval = self._config.polling_interval or POLLING_INTERVAL
        interval = self._to_int_with_check(interval, "polling_interval", 1)
        return interval

    @property
    def timeout(self) -> int:
        """Return the timeout period(sec).

        If not in config file, return the default value.
        """
        timeout = self._config.timeout or TIMEOUT
        timeout = self._to_int_with_check(timeout, "timeout", 1)
        return timeout

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


class Profile(object):
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


class Environment(object):
    def __init__(self, use_env: bool):
        self._use_env = use_env

    def __getattr__(self, name: str) -> Optional[str]:
        if self._use_env:
            return os.getenv(name.upper())
        else:
            return None
