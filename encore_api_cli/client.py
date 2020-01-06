import base64
import hashlib
import json
import time
from pathlib import Path
from textwrap import dedent
from typing import Any, Callable, List, Optional, Tuple, Union
from urllib.parse import urljoin, urlparse

import requests
from yaspin import yaspin

from encore_api_cli.exceptions import InvalidFileType, RequestsError
from encore_api_cli.output import write_http

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
        self.client_id = client_id
        self.client_secret = client_secret

        self.oauth_url = urljoin(base_url, "v1/oauth/accesstokens")
        self.api_url = urljoin(base_url, "anymotion/v1/")

        self.interval = max(1, interval)
        self.max_steps = max(1, timeout // interval)

        self.verbose = verbose

    def upload_to_s3(self, path: Union[str, Path]) -> Tuple[str, str]:
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
        data = {"origin_key": path.name, "content_md5": content_md5}
        url = urljoin(self.api_url, f"{media_type}s/")
        response = self._requests(requests.post, url, data)
        media_id, upload_url = self._parse_response(response, ("id", "upload_url"))
        # Upload to S3
        # TODO: use self._requests
        requests.put(upload_url, path.open("rb"), headers={"Content-MD5": content_md5})

        return media_id, media_type

    def show_list(self, endpoint: str) -> None:
        """Show list."""
        data: List[Any] = []
        url = urljoin(self.api_url, f"{endpoint}/")
        while url:
            response = self._requests(requests.get, url)
            d, url = self._parse_response(response, ("data", "next"))
            data += d
        print(json.dumps(data, indent=4))

    def extract_keypoint_from_image(self, image_id: int) -> int:
        """Extract keypoint using image_id."""
        return self._extract_keypoint({"image_id": image_id})

    def extract_keypoint_from_movie(self, movie_id: int) -> int:
        """Extract keypoint using movie_id."""
        return self._extract_keypoint({"movie_id": movie_id})

    def wait_for_extraction(self, keypoint_id: int) -> str:
        """Wait for extraction."""
        url = urljoin(self.api_url, f"keypoints/{keypoint_id}/")
        status = self._wait_for_done(url)
        return status

    def get_keypoint(self, keypoint_id: int) -> str:
        """Get keypoint using keypoint_id."""
        url = urljoin(self.api_url, f"keypoints/{keypoint_id}/")
        response = self._requests(requests.get, url)
        status, keypoint = self._parse_response(response, ("exec_status", "keypoint"))
        if status == "SUCCESS":
            keypoint = json.loads(keypoint)
            keypoint = json.dumps(keypoint, indent=4)
            return keypoint
        else:
            return "Status is not SUCCESS."

    def get_analysis(self, analysis_id: int) -> str:
        """Get result of analysis using analysis_id."""
        url = urljoin(self.api_url, f"analyses/{analysis_id}/")
        response = self._requests(requests.get, url)
        status, result = self._parse_response(response, ("exec_status", "result"))
        if status == "SUCCESS":
            result = json.loads(result)
            result = json.dumps(result, indent=4)
            return result
        else:
            return "Status is not SUCCESS."

    def draw_keypoint(self, keypoint_id: int) -> Optional[str]:
        """Draw keypoint."""
        url = urljoin(self.api_url, f"drawings/")
        data = {"keypoint_id": keypoint_id}
        response = self._requests(requests.post, url, data=data)
        (drawing_id,) = self._parse_response(response, ("id",))

        print(f"Draw keypoint (drawing_id: {drawing_id})")
        url = urljoin(self.api_url, f"drawings/{drawing_id}/")
        status = self._wait_for_done(url)

        drawing_url = None
        if status == "SUCCESS":
            response = self._requests(requests.get, url)
            (drawing_url,) = self._parse_response(response, ("drawing_url",))
            print("Keypoint drawing is complete.")
        elif status == "FAILURE":
            print("Keypoint drawing failed.")
        else:
            print("Keypoint drawing is timed out.")

        return drawing_url

    def analyze_keypoint(self, keypoint_id: int) -> Optional[str]:
        """Analyze keypoint."""
        url = urljoin(self.api_url, f"analyses/")
        data = {"keypoint_id": keypoint_id}
        response = self._requests(requests.post, url, data=data)
        (analysis_id,) = self._parse_response(response, ("id",))

        print(f"Analyze keypoint (analysis_id: {analysis_id})")
        url = urljoin(self.api_url, f"analyses/{analysis_id}/")
        status = self._wait_for_done(url)

        result = None
        if status == "SUCCESS":
            response = self._requests(requests.get, url)
            (result,) = self._parse_response(response, ("result",))
            print("Keypoint analysis is complete.")
        elif status == "FAILURE":
            print("Keypoint analysis failed.")
        else:
            print("Keypoint analysis is timed out.")

        return result

    def download(self, url: str, out_dir: Union[str, Path]) -> None:
        """Download file."""
        if isinstance(out_dir, str):
            out_dir = Path(out_dir)

        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / Path(urlparse(url).path).name

        response = self._requests(requests.get, url, headers={})
        with path.open("wb") as f:
            f.write(response.content)

        print(f"Downloaded the file to {path}.")

    def _create_md5(self, path: Path) -> str:
        with path.open("rb") as f:
            md5 = hashlib.md5(f.read()).digest()
            encoded_content_md5 = base64.b64encode(md5)
            content_md5 = encoded_content_md5.decode()
        return content_md5

    def _extract_keypoint(self, data: dict) -> int:
        """Extract keypoint.

        Raises:
            RequestsError: Exception raised in _requests function.
        """
        url = urljoin(self.api_url, "keypoints/")
        response = self._requests(requests.post, url, data)
        (keypoint_id,) = self._parse_response(response, ("id",))
        return keypoint_id

    def _requests(
        self,
        requests_func: Callable,
        url: str,
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> requests.models.Response:
        """Make a requests to AnyMotion API or Amazon S3.

        Raises:
            RequestsError
        """
        method = requests_func.__name__.upper()
        if headers is None:
            headers = self._get_headers(with_content_type=data is not None)

        if self.verbose:
            write_http(url, method, headers, data)

        try:
            response = requests_func(url, json=data, headers=headers)
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
            "clientId": self.client_id,
            "clientSecret": self.client_secret,
        }
        headers = {"Content-Type": "application/json"}
        response = self._requests(requests.post, self.oauth_url, data, headers)
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
                f"File {path} must have a {', '.join(suffix[:-1])} "
                f"or {suffix[-1]} extension."
            )
            raise InvalidFileType(message)

    def _is_movie(self, path: Path) -> bool:
        return True if path.suffix in MOVIE_SUFFIXES else False

    def _is_image(self, path: Path) -> bool:
        return True if path.suffix in IMAGE_SUFFIXES else False

    @yaspin(text="Processing...")
    def _wait_for_done(self, url: str) -> str:
        for _ in range(self.max_steps):
            response = self._requests(requests.get, url)
            (status,) = self._parse_response(response, ("exec_status",))
            if status in ["SUCCESS", "FAILURE"]:
                break
            time.sleep(self.interval)
        else:
            status = "TIMEOUT"
        return status
