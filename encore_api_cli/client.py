import base64
import hashlib
import json
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests


class Client(object):

    def __init__(self, token, base_url):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {token}'
        }
        self.interval = 10

    def upload_to_s3(self, path):
        if isinstance(path, str):
            path = Path(path)

        media_type = self._get_media_type(path)
        content_md5 = self._create_md5(path)

        # POST movie
        data = {'origin_key': path.name, 'content_md5': content_md5}
        api_url = urljoin(self.base_url, f'{media_type}s/')
        response = self._requests(requests.post, api_url, data)
        media_id, upload_url = self._parse_response(response,
                                                    ('id', 'upload_url'))
        # PUT S3
        requests.put(upload_url,
                     path.open('rb'),
                     headers={'Content-MD5': content_md5})

        return media_id, media_type

    def extract_keypoint(self, movie_id=None, image_id=None, max_step=60):
        api_url = urljoin(self.base_url, 'keypoints/')

        if movie_id is not None:
            data = {'movie_id': movie_id}
        elif image_id is not None:
            data = {'movie_id': image_id}
        else:
            raise Exception('Either "movie_id" or "image_id" is required.')

        response = self._requests(requests.post, api_url, data)
        keypoint_id, = self._parse_response(response, ('id',))

        print(f'Extract keypoint (keypoint_id: {keypoint_id})')
        api_url = urljoin(self.base_url, f'keypoints/{keypoint_id}/')
        for _ in range(max_step):
            response = self._requests(requests.get, api_url)
            status, = self._parse_response(response, ('exec_status',))
            if status in ['SUCCESS', 'FAILURE']:
                break

            time.sleep(self.interval)
            print('.', end='', flush=True)
        else:
            status = 'TIME_OUT'
        print()

        if status == 'SUCCESS':
            print('Keypoint extraction is complete.')
        elif status == 'FAILURE':
            print('Keypoint extraction failed.')
        else:
            print('Keypoint extraction is timed out.')

    def get_keypoint(self, keypoint_id):
        api_url = urljoin(self.base_url, f'keypoints/{keypoint_id}/')
        response = self._requests(requests.get, api_url)
        status, keypoint = self._parse_response(response,
                                                ('exec_status', 'keypoint'))
        if status == 'SUCCESS':
            return keypoint
        else:
            raise

    def draw_keypoint(self, keypoint_id, rule_id=0, max_step=60):
        api_url = urljoin(self.base_url, f'drawings/')
        data = {'keypoint_id': keypoint_id, 'rule_id': rule_id}
        response = self._requests(requests.post, api_url, data=data)
        drawing_id, = self._parse_response(response, ('id',))

        print(f'Draw keypoint (drawing_id: {drawing_id})')
        api_url = urljoin(self.base_url, f'drawings/{drawing_id}/')
        drawing_url = None
        for _ in range(max_step):
            response = self._requests(requests.get, api_url)
            status, = self._parse_response(response, ('exec_status',))
            if status == 'SUCCESS':
                drawing_url, = self._parse_response(response, ('drawing_url',))
                break
            if status == 'FAILURE':
                break
            time.sleep(self.interval)
            print('.', end='', flush=True)
        else:
            status = 'TIME_OUT'
        print()

        if status == 'SUCCESS':
            print('Keypoint drawing is complete.')
        elif status == 'FAILURE':
            print('Keypoint drawing failed.')
        else:
            print('Keypoint drawing is timed out.')

        return drawing_url

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
        if headers is None:
            headers = self.headers
        data = json.dumps(data)
        response = requests_func(url, data=data, headers=headers)
        if response.status_code in [200, 201]:
            return response
        else:
            print(f'{requests_func.__name__.upper()} {url} is failed.')
            print(f'status code: {response.status_code}')
            print(f'content: {response.content.decode()}')
            exit()

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
            raise

    def _is_movie(self, path):
        movie_suffixs = ['.mp4', '.mov']
        return True if path.suffix in movie_suffixs else False

    def _is_image(self, path):
        image_suffixs = ['.jpg', '.jpeg', '.png']
        return True if path.suffix in image_suffixs else False
