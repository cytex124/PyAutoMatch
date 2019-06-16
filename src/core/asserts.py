from datetime import datetime
import requests
from . import settings


def __get_url(path) -> str:
    return settings.HOST + path


def __get_headers(token=None, json=False) -> dict:
    headers = {
        'app_version': '1020349',
        'platform': 'web',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    }
    if token:
        headers[settings.TOKEN_PREFIX] = token
    if json:
        headers['Content-Type'] = 'application/json'
    return headers


def get_request(url_part, token=None):
    return requests.get(__get_url(url_part), headers=__get_headers(token=token))


def post_request(url_part, data, token=None, json=False):
    if json:
        return requests.post(__get_url(url_part), json=data, headers=__get_headers(token=token, json=json))
    return requests.post(__get_url(url_part), data=data, headers=__get_headers(token=token, json=json))


def get_location_list():
    response = requests.get('https://gist.githubusercontent.com/Miserlou/c5cd8364bf9b2420bb29/raw/2bf258763cdddd704f8ffd3ea9a3e81d25e2c6f6/cities.json')
    return response.json()


def get_datetime(dt) -> datetime:
    return datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.%fZ')
