import re
from . import settings
from .models import User, Location
from .asserts import get_datetime, post
import requests
import robobrowser
import configparser


FB_AUTH = "https://www.facebook.com/v2.6/dialog/oauth?redirect_uri=fb464891386855067%3A%2F%2Fauthorize%2F&display=touch&state=%7B%22challenge%22%3A%22IUUkEUqIGud332lfu%252BMJhxL4Wlc%253D%22%2C%220_auth_logger_id%22%3A%2230F06532-A1B9-4B10-BB28-B29956C71AB1%22%2C%22com.facebook.sdk_client_state%22%3Atrue%2C%223_method%22%3A%22sfvc_auth%22%7D&scope=user_birthday%2Cuser_photos%2Cuser_education_history%2Cemail%2Cuser_relationship_details%2Cuser_friends%2Cuser_work_history%2Cuser_likes&response_type=token%2Csigned_request&default_audience=friends&return_scopes=true&auth_type=rerequest&client_id=464891386855067&ret=login&sdk=ios&logger_id=30F06532-A1B9-4B10-BB28-B29956C71AB1&ext=1470840777&hash=AeZqkIcf-NEW6vBd"


def auth():
    config = configparser.ConfigParser()
    try:
        config.read('auth.ini')
    except Exception:
        raise OSError('No auth.ini found!')
    if 'FACEBOOK' in config:
        fb = config['FACEBOOK']
        user = fb['username']
        pw = fb['password']
        if user and pw:
            fb_token = get_fb_access_token(user, pw)
            fb_id = get_fb_id(fb_token)
            data = get_tinder_token(fb_id, fb_token)
            user = User(
                id=data['user']['_id'],
                age_filter_max=data['user']['age_filter_max'],
                age_filter_min=data['user']['age_filter_min'],
                api_token=data['user']['api_token'],
                banned=data['user']['banned'],
                bio=data['user']['bio'],
                full_name=data['user']['full_name'],
                distance_filter=data['user']['distance_filter'],
                gender=data['user']['gender'],
                gender_filter=data['user']['gender_filter'],
                discoverable=data['user']['discoverable'],
                is_traveling=data['user']['is_traveling'],
                travel_pos=Location(
                    lat=data['user']['travel_pos']['lat'],
                    lon=data['user']['travel_pos']['lon']
                ),
                token=data['token'],
                plus=data['globals']['plus'],
                birthdate=get_datetime(data['user']['birth_date'])
            )
            return user
        else:
            raise ValueError('No Password oder Username/Email found in auth.ini [FACEBOOK]')
    else:
        raise ValueError('[FACEBOOK] Section is needed in auth.ini')


def get_tinder_token(id: str, token: str):
    data = {'facebook_token': token, 'facebook_id': id}
    response = post('/auth', data)
    return response.json()


def get_fb_access_token(email: str, password: str):
    s = robobrowser.RoboBrowser(user_agent=settings.USER_AGENT, parser="lxml")
    s.open(FB_AUTH)
    f = s.get_form()
    f["pass"] = password
    f["email"] = email
    s.submit_form(f)
    f = s.get_form()
    try:
        s.submit_form(f, submit=f.submit_fields['__CONFIRM__'])
        access_token = re.search(
            r"access_token=([\w\d]+)", s.response.content.decode()).groups()[0]
        return access_token
    except Exception as ex:
        print("access token could not be retrieved. Check your username and password.")
        print("Official error: %s" % ex)
        return {"error": "access token could not be retrieved. Check your username and password."}


def get_fb_id(access_token: str):
    if "error" in access_token:
        return {"error": "access token could not be retrieved"}
    """Gets facebook ID from access token"""
    req = requests.get(
        'https://graph.facebook.com/me?access_token=' + access_token)
    return req.json()["id"]