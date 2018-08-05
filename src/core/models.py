from dataclasses import dataclass
from .asserts import get_datetime, get
from datetime import datetime
from singleton_decorator import singleton


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

    def decide_match(self):
        counter = TinderCounter()
        if self.is_hot_or_not():
            response = get('/like/' + self.id, token=self.token)
            result = response.json()
            counter.liked += 1
            if result['match']:
                counter.matches += 1
            print(result)
            print(self.name)
        else:
            response = get('/pass/' + self.id, token=self.token)
            result = response.json()
            counter.disliked += 1
            print(result)
            print(self.name)

    def is_hot_or_not(self):
        return True


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
            raise ValueError('Cant get Recommandation. ' + response.json())
        else:
            response = response.json()
            if 'message' in response and 'recs timeout' in response['message']:
                raise ConnectionRefusedError('Timeout because too much Rec-requests!')
            result = response['results']
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
