from datetime import datetime
import requests
from . import settings


def get_datetime(dt):
    return datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.%fZ')


def url(path):
    return settings.HOST + path


def get_headers(token=None, json=False):
    data = {
        'app_version': '1020349',
        'platform': 'web',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    }
    if token:
        data[settings.TOKEN_PREFIX] = token
    if json:
        data['Content-Type'] =  'application/json'
    return data


def get(url_part, token=None):
    return requests.get(url(url_part), headers=get_headers(token=token))


def post(url_part, data, token=None, json=False):
    if json:
        return requests.post(url(url_part), json=data, headers=get_headers(token=token, json=json))
    return requests.post(url(url_part), data=data, headers=get_headers(token=token, json=json))


def get_location_list():
    response = requests.get('https://gist.githubusercontent.com/Miserlou/c5cd8364bf9b2420bb29/raw/2bf258763cdddd704f8ffd3ea9a3e81d25e2c6f6/cities.json')
    return response.json()
