from textwrap import dedent
from typing import Any, Optional, Union

import requests

from . import InvalidResponse


class Response(object):
    """AnyMotion API Response."""

    def __init__(self, response: requests.Response):
        self.raw = response
        self._status = ""

    @property
    def json(self) -> Any:
        """Get json data."""
        return self.raw.json()

    @property
    def status(self) -> str:
        """Get status."""
        if self._status == "":
            (status,) = self.get(("execStatus",))
            self._status = status
        return self._status

    @status.setter
    def status(self, value) -> None:
        self._status = value

    @property
    def failure_detail(self) -> Optional[str]:
        """Get failure detail."""
        if self.status == "FAILURE":
            (failure_detail,) = self.get(("failureDetail",))
            return failure_detail
        else:
            return None

    def get(self, keys: Union[str, tuple]) -> tuple:
        """Fetch element from response."""
        if isinstance(keys, str):
            keys = (keys,)
        if not all(k in self.json for k in keys):
            message = dedent(
                f"""\
                    Response does NOT contain {keys}
                    response: {self.json}
                """
            )
            raise InvalidResponse(message)
        return tuple(self.json[k] for k in keys)
