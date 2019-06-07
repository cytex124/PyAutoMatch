import re
from . import settings
from .models import User, Location
from .asserts import get_datetime, post, get
import requests
import robobrowser
import configparser
import logging
import shutil


logger = logging.getLogger(__name__)
FB_AUTH = "https://www.facebook.com/v2.6/dialog/oauth?redirect_uri=fb464891386855067%3A%2F%2Fauthorize%2F&scope=user_birthday%2Cuser_photos%2Cuser_education_history%2Cemail%2Cuser_relationship_details%2Cuser_friends%2Cuser_work_history%2Cuser_likes&response_type=token%2Csigned_request&client_id=464891386855067&ret=login&fallback_redirect_uri=221e1158-f2e9-1452-1a05-8983f99f7d6e&ext=1556057433&hash=Aea6jWwMP_tDMQ9y"


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
            # fb_id = get_fb_id(fb_token)
            logging.info("Successful logged in Facebook")
            data = get_tinder_token(fb_token)
            token = data['data']['api_token']
            meta = get_meta_data(token)
            logging.info("Successful logged in Tinder")
            user = User(
                id=meta['user']['_id'],
                age_filter_max=meta['user']['age_filter_max'],
                age_filter_min=meta['user']['age_filter_min'],
                api_token=meta['user']['api_token'],
                banned=False,
                bio=meta['user']['bio'],
                full_name=meta['user']['full_name'],
                distance_filter=meta['user']['distance_filter'],
                gender=meta['user']['gender'],
                gender_filter=meta['user']['gender_filter'],
                discoverable=meta['user']['discoverable'],
                is_traveling=True,
                travel_pos=Location(
                    lat=meta['travel']['travel_pos']['lat'],
                    lon=meta['travel']['travel_pos']['lon']
                ),
                token=token,
                plus=meta['globals']['plus'],
                birthdate=get_datetime(meta['user']['birth_date'])
            )
            logging.info("Logged in as: {}".format(user))
            return user
        else:
            raise ValueError('No Password oder Username/Email found in auth.ini [FACEBOOK]')
    else:
        raise ValueError('[FACEBOOK] Section is needed in auth.ini')


def get_meta_data(token):
    response = get('/meta', token=token)
    return response.json()


def get_tinder_token(token: str):
    data = {'token': token}
    response = post('/v2/auth/login/facebook?locale=de', data, json=True)
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
        # print(browser.response.content.decode())
        return re.search(
            r"access_token=([\w\d]+)", s.response.content.decode()).groups()[0]
    except requests.exceptions.InvalidSchema as browserAddress:
        # print(type(browserAddress))
        return re.search(
            r"access_token=([\w\d]+)", str(browserAddress)).groups()[0]

def get_fb_id(access_token: str):
    if "error" in access_token:
        return {"error": "access token could not be retrieved"}
    req = requests.get('https://graph.facebook.com/me?access_token=' + access_token)
    return req.json()["id"]
