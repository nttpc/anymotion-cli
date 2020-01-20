import base64
import hashlib
import time
from pathlib import Path
from textwrap import dedent
from typing import Callable, List, Optional, Tuple, Union
from urllib.parse import urljoin

import requests

from encore_api_cli.exceptions import InvalidFileType, RequestsError
from encore_api_cli.output import echo_http, spin

MOVIE_SUFFIXES = [".mp4", ".mov"]
IMAGE_SUFFIXES = [".jpg", ".jpeg", ".png"]


class Client(object):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str,
        interval: int,
        timeout: int,
        verbose: bool = False,
    ):
        self._client_id = client_id
        self._client_secret = client_secret

        self._oauth_url = urljoin(base_url, "v1/oauth/accesstokens")
        self._api_url = urljoin(base_url, "anymotion/v1/")

        self._interval = max(1, interval)
        self._max_steps = max(1, timeout // interval)

        self._verbose = verbose

    def get_info(
        self, endpoint: str, endpoint_id: int = None
    ) -> Union[List[dict], dict]:
        """Get infomation."""
        if endpoint_id is None:
            url = urljoin(self._api_url, f"{endpoint}/")
            return self._get_list(url)
        else:
            url = urljoin(self._api_url, f"{endpoint}/{endpoint_id}/")
            return self._get_one(url)

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
        media_id, upload_url = self._parse_response(response, ("id", "uploadUrl"))

        # Upload to S3
        self._requests(
            requests.put,
            upload_url,
            data=path.open("rb"),
            headers={"Content-MD5": content_md5},
        )

        return media_id, media_type

    def extract_keypoint_from_image(self, image_id: int) -> int:
        """Start keypoint extraction for image_id."""
        return self._extract_keypoint({"image_id": image_id})

    def extract_keypoint_from_movie(self, movie_id: int) -> int:
        """Start keypoint extraction for movie_id."""
        return self._extract_keypoint({"movie_id": movie_id})

    def draw_keypoint(self, keypoint_id: int, rule: Optional[list] = None) -> int:
        """Start drawing for keypoint_id."""
        url = urljoin(self._api_url, f"drawings/")
        json = {"keypoint_id": keypoint_id}
        if rule is not None:
            json["rule"] = rule  # type: ignore
        response = self._requests(requests.post, url, json=json)
        (drawing_id,) = self._parse_response(response, ("id",))
        return drawing_id

    def analyze_keypoint(self, keypoint_id: int, rule: Optional[list] = None) -> int:
        """Start analyze for keypoint_id."""
        url = urljoin(self._api_url, f"analyses/")
        response = self._requests(
            requests.post, url, json={"keypoint_id": keypoint_id, "rule": rule}
        )
        (analysis_id,) = self._parse_response(response, ("id",))
        return analysis_id

    def wait_for_extraction(self, keypoint_id: int) -> str:
        """Wait for extraction."""
        url = urljoin(self._api_url, f"keypoints/{keypoint_id}/")
        status = self._wait_for_done(url)
        return status

    def wait_for_drawing(self, drawing_id: int) -> Tuple[str, Optional[str]]:
        """Wait for drawing."""
        url = urljoin(self._api_url, f"drawings/{drawing_id}/")
        status = self._wait_for_done(url)
        drawing_url = None
        if status == "SUCCESS":
            response = self._requests(requests.get, url)
            (drawing_url,) = self._parse_response(response, ("drawingUrl",))
        return status, drawing_url

    def wait_for_analysis(self, analysis_id: int) -> str:
        """Wait for analysis."""
        url = urljoin(self._api_url, f"analyses/{analysis_id}/")
        status = self._wait_for_done(url)
        return status

    def download(self, url: str, path: Path) -> None:
        """Download file from url."""
        response = self._requests(requests.get, url, headers={})
        with path.open("wb") as f:
            f.write(response.content)

    def _create_md5(self, path: Path) -> str:
        with path.open("rb") as f:
            md5 = hashlib.md5(f.read()).digest()
            encoded_content_md5 = base64.b64encode(md5)
            content_md5 = encoded_content_md5.decode()
        return content_md5

    def _get_one(self, url: str) -> dict:
        response = self._requests(requests.get, url)
        return response.json()

    @spin(text="Retrieving...")
    def _get_list(self, url: str) -> List[dict]:
        data: List[dict] = []
        while url:
            response = self._requests(requests.get, url)
            sub_data, url = self._parse_response(response, ("data", "next"))
            data += sub_data
        return data

    def _extract_keypoint(self, data: dict) -> int:
        """Extract keypoint.

        Raises:
            RequestsError: Exception raised in _requests function.
        """
        url = urljoin(self._api_url, "keypoints/")
        response = self._requests(requests.post, url, json=data)
        (keypoint_id,) = self._parse_response(response, ("id",))
        return keypoint_id

    def _requests(
        self,
        requests_func: Callable,
        url: str,
        json: Optional[dict] = None,
        data: Optional[object] = None,
        headers: Optional[dict] = None,
    ) -> requests.models.Response:
        """Make a requests to AnyMotion API or Amazon S3.

        Raises:
            RequestsError
        """
        method = requests_func.__name__.upper()
        is_json = json is not None

        if headers is None:
            headers = self._get_headers(with_content_type=is_json)

        if self._verbose:
            echo_http(url, method, headers, json)

        try:
            if is_json:
                response = requests_func(url, json=json, headers=headers)
            else:
                response = requests_func(url, data=data, headers=headers)
        except requests.exceptions.ConnectionError:
            message = f"{method} {url} is failed."
            raise RequestsError(message)

        if response.status_code not in [200, 201]:
            message = dedent(
                f"""\
                    {method} {url} is failed.
                    status code: {response.status_code}
                    content: {response.content.decode()}
                """
            )
            raise RequestsError(message)

        return response

    def _get_headers(self, with_content_type: bool = True) -> dict:
        """Generate Authorization and Content-Type headers."""
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
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
        (token,) = self._parse_response(response, ("accessToken",))

        return token

    def _parse_response(self, response: requests.models.Response, keys: tuple) -> tuple:
        res = response.json()
        if not all(k in res for k in keys):
            print(f"Response does NOT contain {keys}")
            print(f"response: {res}")
            raise Exception("Invalid response")
        return tuple(res[k] for k in keys)

    def _get_media_type(self, path: Path) -> str:
        if self._is_movie(path):
            return "movie"
        elif self._is_image(path):
            return "image"
        else:
            suffix = MOVIE_SUFFIXES + IMAGE_SUFFIXES
            message = (
                f"The extension of the file {path} must be"
                f"{', '.join(suffix[:-1])} or {suffix[-1]}."
            )
            raise InvalidFileType(message)

    def _is_movie(self, path: Path) -> bool:
        return True if path.suffix.lower() in MOVIE_SUFFIXES else False

    def _is_image(self, path: Path) -> bool:
        return True if path.suffix.lower() in IMAGE_SUFFIXES else False

    @spin(text="Processing...")
    def _wait_for_done(self, url: str) -> str:
        for _ in range(self._max_steps):
            response = self._requests(requests.get, url)
            (status,) = self._parse_response(response, ("execStatus",))
            if status in ["SUCCESS", "FAILURE"]:
                break
            time.sleep(self._interval)
        else:
            status = "TIMEOUT"
        return status
