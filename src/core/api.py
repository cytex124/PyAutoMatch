import requests
from . import settings


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


def get_tinder_token(id: str, token: str):
    data = {'facebook_token': token, 'facebook_id': id}
    response = requests.post(url('/auth'), data=data, headers=get_headers(), json=True)
    return response.json()



