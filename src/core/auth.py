import re
from . import settings
from .models import User, Location
from .asserts import get_datetime, post_request, get_request
import requests
import robobrowser
import configparser
import logging


logger = logging.getLogger(__name__)
FB_AUTH = "https://www.facebook.com/v2.6/dialog/oauth?redirect_uri=fb464891386855067%3A%2F%2Fauthorize%2F&scope=user_birthday%2Cuser_photos%2Cuser_education_history%2Cemail%2Cuser_relationship_details%2Cuser_friends%2Cuser_work_history%2Cuser_likes&response_type=token%2Csigned_request&client_id=464891386855067&ret=login&fallback_redirect_uri=221e1158-f2e9-1452-1a05-8983f99f7d6e&ext=1556057433&hash=Aea6jWwMP_tDMQ9y"


def auth_with_facebook_on_tinder() -> User:
    config = _get_auth_ini_data()
    # Check Facebook section
    if 'FACEBOOK' not in config:
        raise ValueError('[FACEBOOK] Section is needed in auth.ini')

    user = config['FACEBOOK']['username']
    pw = config['FACEBOOK']['password']

    # Check User and pw
    if user and pw:
        # Get Tinder token from fb account
        token = _login_as_fb_user_and_get_tinder_token(user, pw)
        logging.info("Successful logged in Tinder")
        # Get User Info and account info
        meta = _get_tinder_meta_data(token)
        user = meta['user']
        logging.info("Successful got Meta-Data from Tinder")
        # Create user with meta data
        user = User(
            id=user['_id'],
            age_filter_max=user['age_filter_max'],
            age_filter_min=user['age_filter_min'],
            api_token=user['api_token'],
            banned=False,
            bio=user['bio'],
            full_name=user['full_name'],
            distance_filter=user['distance_filter'],
            gender=user['gender'],
            gender_filter=user['gender_filter'],
            discoverable=user['discoverable'],
            is_traveling=True,
            travel_pos=Location(
                lat=meta['travel']['travel_pos']['lat'],
                lon=meta['travel']['travel_pos']['lon']
            ),
            token=token,
            plus=meta['globals']['plus'],
            birthdate=get_datetime(user['birth_date'])
        )
        logging.info("Logged in as: {}".format(user))
        return user
    else:
        raise ValueError('No Password oder Username/Email found in auth.ini [FACEBOOK]')


def _get_auth_ini_data() -> dict:
    """
    Load auth.ini file
    :return: dict
    """
    config = configparser.ConfigParser()
    try:
        config.read('auth.ini')
        config.sections()
        return config
    except Exception:
        raise OSError('No auth.ini found!')


def _login_as_fb_user_and_get_tinder_token(user: str, pw: str) -> str:
    """
    Use user/mail and pw to login into fb and tinder to get tinder access token
    :param user: str
    :param pw: str
    :return: token: str
    """
    fb_token = _get_fb_access_token(user, pw)
    # fb_id = get_fb_id(fb_token)
    logging.info("Successful logged in Facebook")
    tinder_data = _get_tinder_token(fb_token)
    return tinder_data['data']['api_token']


def _get_fb_access_token(email: str, password: str) -> str:
    s = robobrowser.RoboBrowser(user_agent=settings.USER_AGENT, parser="lxml")
    s.open(FB_AUTH)
    f = s.get_form()
    f["pass"] = password
    f["email"] = email
    s.submit_form(f)
    f = s.get_form()
    try:
        s.submit_form(f, submit=f.submit_fields['__CONFIRM__'])
        return re.search(r"access_token=([\w\d]+)", s.response.content.decode()).groups()[0]
    except requests.exceptions.InvalidSchema as browserAddress:
        return re.search(r"access_token=([\w\d]+)", str(browserAddress)).groups()[0]


def _get_tinder_token(token: str) -> dict:
    response = post_request('/v2/auth/login/facebook?locale=de', {'token': token}, json=True)
    return response.json()


def _get_tinder_meta_data(token: str) -> dict:
    response = get_request('/meta', token=token)
    return response.json()
