from datetime import datetime
import requests
from . import settings


def get_datetime(dt):
    return datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.%fZ')


def url(path):
    return settings.HOST + path


def get_headers(token=None):
    data = {
        'app_version': '6.9.4',
        'platform': 'ios',
        'User-Agent': settings.USER_AGENT,
    }
    if token:
        data[settings.TOKEN_PREFIX] = token
    return data


def get(url_part, token=None):
    return requests.get(url(url_part), headers=get_headers(token=token))


def post(url_part, data, token=None):
    return requests.post(url(url_part), data=data, headers=get_headers(token=token))


def get_location_list():
    response = requests.get('https://gist.githubusercontent.com/Miserlou/c5cd8364bf9b2420bb29/raw/2bf258763cdddd704f8ffd3ea9a3e81d25e2c6f6/cities.json')
    return response.json()
