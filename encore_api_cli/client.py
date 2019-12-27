import base64
import hashlib
import json
from pathlib import Path
from textwrap import dedent
import time
from urllib.parse import urljoin
from urllib.parse import urlparse

import requests

from encore_api_cli.exceptions import InvalidFileType
from encore_api_cli.exceptions import RequestsError

MOVIE_SUFFIXES = ['.mp4', '.mov']
IMAGE_SUFFIXES = ['.jpg', '.jpeg', '.png']


class Client(object):
    def __init__(self,
                 client_id,
                 client_secret,
                 base_url,
                 interval=10,
                 timeout=600):
        self.client_id = client_id
        self.client_secret = client_secret

        self.oauth_url = urljoin(base_url, 'v1/oauth/accesstokens')
        self.api_url = urljoin(base_url, 'anymotion/v1/')

        self.interval = interval
        self.max_steps = timeout // interval

    def upload_to_s3(self, path):
        """Upload movie or image to Amazon S3

        Args:
            path (str or Path)

        Returns:
            str: Created image_id or movie_id.
            str: image or movie

        Raises:
            InvalidFileType: Exception raised in _get_media_type function.
            RequestsError: Exception raised in _requests function.
        """
        if isinstance(path, str):
            path = Path(path)

        media_type = self._get_media_type(path)
        content_md5 = self._create_md5(path)

        # Register movie or image
        data = {'origin_key': path.name, 'content_md5': content_md5}
        url = urljoin(self.api_url, f'{media_type}s/')
        response = self._requests(requests.post, url, data)
        media_id, upload_url = self._parse_response(response,
                                                    ('id', 'upload_url'))
        # Upload to S3
        # TODO(y_kumiha): use self._requests
        requests.put(upload_url,
                     path.open('rb'),
                     headers={'Content-MD5': content_md5})

        return media_id, media_type

    def show_list(self, endpoint):
        data = []
        url = urljoin(self.api_url, f'{endpoint}/')
        while url:
            response = self._requests(requests.get, url)
            d, url = self._parse_response(response, ('data', 'next'))
            data += d
        data = json.dumps(data, indent=4)
        print(data)

    def extract_keypoint(self, movie_id=None, image_id=None):
        url = urljoin(self.api_url, 'keypoints/')

        if movie_id is not None:
            data = {'movie_id': movie_id}
        elif image_id is not None:
            data = {'image_id': image_id}
        else:
            raise Exception('Either "movie_id" or "image_id" is required.')

        response = self._requests(requests.post, url, data)
        keypoint_id, = self._parse_response(response, ('id', ))

        print(f'Extract keypoint (keypoint_id: {keypoint_id})')
        url = urljoin(self.api_url, f'keypoints/{keypoint_id}/')
        status = self._wait_for_done(url)

        if status == 'SUCCESS':
            print('Keypoint extraction is complete.')
        elif status == 'FAILURE':
            print('Keypoint extraction failed.')
        else:
            print('Keypoint extraction is timed out.')

        return keypoint_id

    def get_keypoint(self, keypoint_id):
        url = urljoin(self.api_url, f'keypoints/{keypoint_id}/')
        response = self._requests(requests.get, url)
        status, keypoint = self._parse_response(response,
                                                ('exec_status', 'keypoint'))
        if status == 'SUCCESS':
            keypoint = json.loads(keypoint)
            keypoint = json.dumps(keypoint, indent=4)
            return keypoint
        else:
            return 'Status is not SUCCESS.'

    def get_analysis(self, analysis_id):
        url = urljoin(self.api_url, f'analyses/{analysis_id}/')
        response = self._requests(requests.get, url)
        status, result = self._parse_response(response,
                                              ('exec_status', 'result'))
        if status == 'SUCCESS':
            result = json.loads(result)
            result = json.dumps(result, indent=4)
            return result
        else:
            return 'Status is not SUCCESS.'

    def draw_keypoint(self, keypoint_id):
        url = urljoin(self.api_url, f'drawings/')
        data = {'keypoint_id': keypoint_id}
        response = self._requests(requests.post, url, data=data)
        drawing_id, = self._parse_response(response, ('id', ))

        print(f'Draw keypoint (drawing_id: {drawing_id})')
        url = urljoin(self.api_url, f'drawings/{drawing_id}/')
        status = self._wait_for_done(url)

        drawing_url = None
        if status == 'SUCCESS':
            response = self._requests(requests.get, url)
            drawing_url, = self._parse_response(response, ('drawing_url', ))
            print('Keypoint drawing is complete.')
        elif status == 'FAILURE':
            print('Keypoint drawing failed.')
        else:
            print('Keypoint drawing is timed out.')

        return drawing_url

    def analyze_keypoint(self, keypoint_id):
        url = urljoin(self.api_url, f'analyses/')
        data = {'keypoint_id': keypoint_id}
        response = self._requests(requests.post, url, data=data)
        analysis_id, = self._parse_response(response, ('id', ))

        print(f'Analyze keypoint (analysis_id: {analysis_id})')
        url = urljoin(self.api_url, f'analyses/{analysis_id}/')
        status = self._wait_for_done(url)

        result = None
        if status == 'SUCCESS':
            response = self._requests(requests.get, url)
            result, = self._parse_response(response, ('result', ))
            print('Keypoint analysis is complete.')
        elif status == 'FAILURE':
            print('Keypoint analysis failed.')
        else:
            print('Keypoint analysis is timed out.')

        return result

    def download(self, url, out_dir):
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / Path(urlparse(url).path).name

        response = self._requests(requests.get, url, headers={})
        with path.open('wb') as f:
            f.write(response.content)

        print(f'Downloaded the file to {path}.')

    def _create_md5(self, path):
        with path.open('rb') as f:
            md5 = hashlib.md5(f.read()).digest()
            encoded_content_md5 = base64.b64encode(md5)
            content_md5 = encoded_content_md5.decode()
        return content_md5

    def _requests(self, requests_func, url, data=None, headers=None):
        """Make a requests to AnyMotion API or Amazon S3.

        Raises:
            RequestsError
        """
        if headers is None:
            headers = self._get_headers(with_content_type=data)
        data = json.dumps(data)

        try:
            response = requests_func(url, data=data, headers=headers)
        except requests.exceptions.ConnectionError:
            message = f'{requests_func.__name__.upper()} {url} is failed.'
            raise RequestsError(message)

        if response.status_code not in [200, 201]:
            message = dedent(f"""\
                {requests_func.__name__.upper()} {url} is failed.
                status code: {response.status_code}
                content: {response.content.decode()}
            """)
            raise RequestsError(message)

        return response

    def _get_headers(self, with_content_type=True):
        """Generate Authorization and Content-Type headers."""
        token = self._get_token()
        headers = {'Authorization': f'Bearer {token}'}
        if with_content_type:
            headers['Content-Type'] = 'application/json'
        return headers

    def _get_token(self):
        """Get a token using client ID and secret."""
        data = {
            'grantType': 'client_credentials',
            'clientId': self.client_id,
            'clientSecret': self.client_secret
        }
        headers = {'Content-Type': 'application/json'}
        response = self._requests(requests.post, self.oauth_url, data, headers)
        token, = self._parse_response(response, ('accessToken', ))

        return token

    def _parse_response(self, response, keys):
        response = response.json()
        if not all(k in response for k in keys):
            print(f'Response does NOT contain {keys}')
            print(f'response: {response}')
            raise Exception('Invalid response')
        return (response[k] for k in keys)

    def _get_media_type(self, path):
        if self._is_movie(path):
            return 'movie'
        elif self._is_image(path):
            return 'image'
        else:
            suffix = MOVIE_SUFFIXES + IMAGE_SUFFIXES
            message = (f"File {path} must have a {', '.join(suffix[:-1])} "
                       f"or {suffix[-1]} extension.")
            raise InvalidFileType(message)

    def _is_movie(self, path):
        return True if path.suffix in MOVIE_SUFFIXES else False

    def _is_image(self, path):
        return True if path.suffix in IMAGE_SUFFIXES else False

    def _wait_for_done(self, url):
        for _ in range(self.max_steps):
            response = self._requests(requests.get, url)
            status, = self._parse_response(response, ('exec_status', ))
            if status in ['SUCCESS', 'FAILURE']:
                break

            time.sleep(self.interval)
            print('.', end='', flush=True)
        else:
            status = 'TIME_OUT'
        print()

        return status
