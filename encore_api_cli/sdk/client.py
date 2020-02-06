import base64
import hashlib
import time
from pathlib import Path
from textwrap import dedent
from typing import Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin, urlparse, urlunparse

import requests

from . import InvalidFileType, RequestsError
from .response import Response

MOVIE_SUFFIXES = [".mp4", ".mov"]
IMAGE_SUFFIXES = [".jpg", ".jpeg", ".png"]


class Client(object):
    """API Client for the AnyMotion API.

    All HTTP requests for the AnyMotion API (including Amazon S3) are handled by this
    class.
    The acquired data should not be displayed. Should be displayed for each command.

    Attributes:
        token (str): access token for authentication.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        api_url: str = "https://api.customer.jp/anymotion/v1/",
        interval: int = 5,
        timeout: int = 600,
        verbose: bool = False,
        echo_request: Optional[Callable] = None,
        echo_response: Optional[Callable] = None,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._token = None

        self._set_url(api_url)

        self._interval = max(1, interval)
        self._max_steps = max(1, timeout // self._interval)

        self._verbose = verbose
        self._echo_request = echo_request
        self._echo_response = echo_response

    @property
    def token(self) -> str:
        """Return access token."""
        return self._token or self._get_token()

    def get_one_data(self, endpoint: str, endpoint_id: int) -> dict:
        """Get one piece of data from AnyMotion API."""
        url = urljoin(self._api_url, f"{endpoint}/{endpoint_id}/")
        response = self._requests(requests.get, url)
        return response.json

    def get_list_data(self, endpoint: str, params: Optional[dict] = None) -> List[dict]:
        """Get list data from AnyMotion API."""
        url = urljoin(self._api_url, f"{endpoint}/")
        data: List[dict] = []
        while url:
            response = self._requests(requests.get, url, params=params)
            sub_data, url = response.get(("data", "next"))
            data += sub_data
        return data

    def upload_to_s3(self, path: Union[str, Path]) -> Tuple[int, str]:
        """Upload movie or image to Amazon S3.

        Args:
            path: The path of the file to upload.

        Returns:
            A tuple of media_id and media_type. media_id is the created image_id or
            movie_id. media_type is the string of "image" or "movie".

        Raises:
            InvalidFileType: Exception raised in _get_media_type function.
            RequestsError: Exception raised in _requests function.
        """
        if isinstance(path, str):
            path = Path(path)

        media_type = self._get_media_type(path)
        content_md5 = self._create_md5(path)

        # Register movie or image
        response = self._requests(
            requests.post,
            urljoin(self._api_url, f"{media_type}s/"),
            json={"origin_key": path.name, "content_md5": content_md5},
        )
        media_id, upload_url = response.get(("id", "uploadUrl"))

        # Upload to S3
        self._requests(
            requests.put,
            upload_url,
            data=path.open("rb"),
            headers={"Content-MD5": content_md5},
        )

        return media_id, media_type

    def extract_keypoint_from_image(self, image_id: int) -> int:
        """Start keypoint extraction for image_id.

        Returns:
            keypoint_id.
        """
        return self._extract_keypoint({"image_id": image_id})

    def extract_keypoint_from_movie(self, movie_id: int) -> int:
        """Start keypoint extraction for movie_id.

        Returns:
            keypoint_id.
        """
        return self._extract_keypoint({"movie_id": movie_id})

    def draw_keypoint(
        self, keypoint_id: int, rule: Optional[Union[list, dict]] = None
    ) -> int:
        """Start drawing for keypoint_id."""
        url = urljoin(self._api_url, f"drawings/")
        json: Dict[str, Union[int, list, dict]] = {"keypoint_id": keypoint_id}
        if rule is not None:
            json["rule"] = rule
        response = self._requests(requests.post, url, json=json)
        (drawing_id,) = response.get("id")
        return drawing_id

    def analyze_keypoint(self, keypoint_id: int, rule: Union[list, dict]) -> int:
        """Start analyze for keypoint_id."""
        url = urljoin(self._api_url, f"analyses/")
        json: Dict[str, Union[int, list, dict]] = {"keypoint_id": keypoint_id}
        if rule is not None:
            json["rule"] = rule
        response = self._requests(requests.post, url, json=json)
        (analysis_id,) = response.get("id")
        return analysis_id

    def wait_for_extraction(self, keypoint_id: int) -> Response:
        """Wait for extraction."""
        url = urljoin(self._api_url, f"keypoints/{keypoint_id}/")
        response = self._wait_for_done(url)
        return response

    def wait_for_drawing(self, drawing_id: int) -> Tuple[str, Optional[str]]:
        """Wait for drawing."""
        url = urljoin(self._api_url, f"drawings/{drawing_id}/")
        response = self._wait_for_done(url)
        drawing_url = None
        if response.status == "SUCCESS":
            (drawing_url,) = response.get("drawingUrl")
        return response.status, drawing_url

    def wait_for_analysis(self, analysis_id: int) -> Response:
        """Wait for analysis."""
        url = urljoin(self._api_url, f"analyses/{analysis_id}/")
        response = self._wait_for_done(url)
        return response

    def download(self, url: str, path: Path) -> None:
        """Download file from url."""
        response = self._requests(requests.get, url, headers={})
        with path.open("wb") as f:
            f.write(response.raw.content)

    def _create_md5(self, path: Path) -> str:
        with path.open("rb") as f:
            md5 = hashlib.md5(f.read()).digest()
            encoded_content_md5 = base64.b64encode(md5)
            content_md5 = encoded_content_md5.decode()
        return content_md5

    def _extract_keypoint(self, data: dict) -> int:
        """Start keypoint extraction.

        Raises:
            RequestsError: Exception raised in _requests function.
        """
        url = urljoin(self._api_url, "keypoints/")
        response = self._requests(requests.post, url, json=data)
        (keypoint_id,) = response.get("id")
        return keypoint_id

    def _requests(
        self,
        requests_func: Callable,
        url: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        data: Optional[object] = None,
        headers: Optional[dict] = None,
    ) -> Response:
        """Send an HTTP requests to the AnyMotion API or Amazon S3 and receive a response.

        Raises:
            RequestsError
        """
        method = requests_func.__name__.upper()
        is_json = json is not None

        if headers is None:
            headers = self._get_headers(with_content_type=is_json)

        if self._verbose and self._echo_request:
            # TODO: add params
            self._echo_request(url, method, headers, json)

        try:
            if is_json:
                response = requests_func(url, params=params, json=json, headers=headers)
            else:
                response = requests_func(url, params=params, data=data, headers=headers)
        except requests.exceptions.ConnectionError:
            message = f"{method} {url} is failed."
            raise RequestsError(message)

        if self._verbose and self._echo_response:
            self._echo_response(
                response.status_code,
                response.reason,
                response.raw.version,
                response.headers,
                response.json(),
            )

        if response.status_code not in [200, 201]:
            message = dedent(
                f"""\
                    {method} {url} is failed.
                    status code: {response.status_code}
                    content: {response.content.decode()}
                """
            )
            raise RequestsError(message)

        return Response(response)

    def _get_headers(self, with_content_type: bool = True) -> dict:
        """Generate Authorization and Content-Type headers."""
        headers = {"Authorization": f"Bearer {self.token}"}
        if with_content_type:
            headers["Content-Type"] = "application/json"
        return headers

    def _get_token(self) -> str:
        """Get a token using client ID and secret."""
        data = {
            "grantType": "client_credentials",
            "clientId": self._client_id,
            "clientSecret": self._client_secret,
        }
        response = self._requests(
            requests.post,
            self._oauth_url,
            json=data,
            headers={"Content-Type": "application/json"},
        )
        (token,) = response.get("accessToken")

        self._token = token
        return token

    def _get_media_type(self, path: Path) -> str:
        if path.suffix.lower() in MOVIE_SUFFIXES:
            return "movie"
        elif path.suffix.lower() in IMAGE_SUFFIXES:
            return "image"
        else:
            suffix = MOVIE_SUFFIXES + IMAGE_SUFFIXES
            message = (
                f"The extension of the file {path} must be"
                f"{', '.join(suffix[:-1])} or {suffix[-1]}."
            )
            raise InvalidFileType(message)

    def _wait_for_done(self, url: str) -> Response:
        for _ in range(self._max_steps):
            response = self._requests(requests.get, url)
            if response.status in ["SUCCESS", "FAILURE"]:
                break
            time.sleep(self._interval)
        else:
            response.status = "TIMEOUT"
        return response

    def _set_url(self, api_url: str) -> None:
        parts = urlparse(api_url)
        if parts.path[-1] != "/":
            parts.path += "/"

        self._api_url = urlunparse((parts.scheme, parts.netloc, parts.path, "", "", ""))
        self._oauth_url = urlunparse(
            (parts.scheme, parts.netloc, "v1/oauth/accesstokens", "", "", "")
        )
