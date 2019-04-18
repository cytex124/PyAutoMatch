from dataclasses import dataclass
from .asserts import get_datetime, get, post, url
from datetime import datetime
from singleton_decorator import singleton
import geocoder
import logging
import os
import requests
import shutil


logger = logging.getLogger(__name__)
FILTER_TRANS_FILE = open(os.path.join('filters', 'trans.txt'), "r")
FILTER_TRANS = [x.strip() for x in FILTER_TRANS_FILE.readlines()]
FILTER_TRANS_FILE.close()
DOWNLOAD_FOLDER = os.path.join('downloads')


@singleton
class TinderCounter:

    def __init__(self):
        self.matches = 0
        self.liked = 0
        self.disliked = 0

    def __str__(self):
        return 'TinderCounter: {} matches, {} liked, {} disliked'.format(self.matches, self.liked, self.disliked)


@dataclass
class Location:
    lat: float
    lon: float

    def get_location_name(self):
        data = geocoder.google((self.lat, self.lon), method='reverse')
        return '{}, {}'.format(data.city, data.country_long)


@dataclass
class Recommendation:
    id: str
    token: str
    distance_mi: int
    name: str
    bio: str
    birth_date: datetime
    photo_urls: list
    gender: int

    def decide_match(self, args):
        if self.is_hot_or_not() and self.check_args_filter(args):
            self.like()
            if args.savepics:
                self.download_pic()
        else:
            self.dislike()

    def like(self):
        counter = TinderCounter()
        response = get('/like/' + self.id, token=self.token)
        result = response.json()
        counter.liked += 1
        if result['match']:
            counter.matches += 1
        logger.info('Liked: {} {}'.format(self.name, self.photo_urls[0]))

    def dislike(self):
        counter = TinderCounter()
        _ = get('/pass/' + self.id, token=self.token)
        counter.disliked += 1
        logger.info('Disliked: {} {}'.format(self.name, self.photo_urls[0]))

    def is_hot_or_not(self):
        return True

    def check_args_filter(self, args):
        if args.notrans:
            for trans_word in FILTER_TRANS:
                if trans_word in self.bio:
                    return False
        return True

    def download_pic(self):
        r = requests.get(self.photo_urls[0], stream=True)
        if r.status_code == 200:
            with open(os.path.join(DOWNLOAD_FOLDER, '{}.jpg'.format(self.id)), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

@dataclass
class User:
    id: str
    api_token: str
    token: str
    banned: bool
    is_traveling: bool
    plus: bool

    age_filter_max: int
    age_filter_min: int
    distance_filter: int
    gender_filter: int
    discoverable: bool
    travel_pos: Location

    full_name: str
    bio: str
    gender: int
    birthdate: datetime

    def get_match_recommendations(self):
        response = get('/user/recs', token=self.token)
        if response.status_code != 200:
            if response.status_code == 500:
                raise SystemError('Tinder has some trouble right now! Don´t worry try it later again!')
            else:
                raise ValueError('Cant get Recommandation. {}'.format( response.json() ))
        else:
            response = response.json()
            if 'message' in response and 'recs timeout' in response['message']:
                raise ConnectionRefusedError('Timeout because too much Rec-requests!')
            results = response['results']
            recs = []
            for result in results:
                photo_urls = []
                for photo in result['photos']:
                    photo_urls.append(photo['url'])
                recs.append(Recommendation(
                    id=result['_id'],
                    distance_mi=result['distance_mi'],
                    name=result['name'],
                    bio=result['bio'],
                    birth_date=get_datetime(result['birth_date']),
                    photo_urls=photo_urls,
                    gender=result['gender'],
                    token=self.token
                ))
            return recs

    def change_location(self, lat: float, lon: float):
        _ = post('/user/ping', data={'lat': lat, 'lon': lon}, token=self.token)
        logger.info("Changed Location to {}".format(self.travel_pos.get_location_name()))

    def refresh(self):
        pass

    def __str__(self):
        location_name = self.travel_pos.get_location_name()
        if location_name == 'None, None':
            location_name = 'Unknown'
        return '{} - {} - {} - Banned: {} - Find Partner between {}-{} in Distance of {} km in {} with Gender {}'.format(
            self.full_name, 'F' if self.gender else 'M', 'PLUS' if self.plus else 'Not PLUS',
            'YES' if self.banned else 'NO', self.age_filter_min,
            self.age_filter_max, self.distance_filter, location_name,
            'F' if self.gender_filter else 'M')
