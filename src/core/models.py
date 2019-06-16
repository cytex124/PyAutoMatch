from dataclasses import dataclass
from .asserts import get_datetime, get_request, post_request
from datetime import datetime, timedelta
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
    instagram_urls: list
    video_urls: list
    gender: int

    def decide_match(self, notrans, savepics):
        """
        Decide if it is a match
        :param notrans: boolean --> If true no Transgenders will be matched (by text). txt-filter-file is under src/filters/trans.txt
        :param savepics: boolean --> If true pics, videos and instapics will be downloaded to src/downloads
        :return: none
        """
        if self.is_hot_or_not() and self.is_not_in_filter_options(notrans):
            self.like()
            if savepics:
                self.download_pics_and_videos()
        else:
            self.dislike()

    def like(self):
        """
        Like a recommendation. Increases counter.
        :return: none
        """
        counter = TinderCounter()
        response = get_request('/like/' + self.id, token=self.token)
        result = response.json()
        counter.liked += 1
        if result['match']:
            counter.matches += 1
        try:
            logger.info('Liked: {} {}'.format(self.name, self.photo_urls[0]))
        except IndexError:
            logger.info('Liked: {}'.format(self.name))

    def dislike(self):
        """
        Dislike a recommendation. Decreases counter.
        :return: none
        """
        counter = TinderCounter()
        _ = get_request('/pass/' + self.id, token=self.token)
        counter.disliked += 1
        logger.info('Disliked: {} {}'.format(self.name, self.photo_urls[0]))

    def is_hot_or_not(self):
        """
        Decide if person is hot or not.
        Likes everything at this moment.
        :return: boolean --> If person is hot or not.
        """
        # TODO: Need AI here :D
        return True

    def is_not_in_filter_options(self, no_trans):
        """
        Checks filter options. If everything is fine --> True
        :param no_trans: boolean --> Transgender filter
        :return: boolean
        """
        # Trans filter
        if no_trans:
            for trans_word in FILTER_TRANS:
                if trans_word in self.bio:
                    return False
        return True

    def download_pics_and_videos(self):
        """
        Downloads Pics and Videos of recommendation.
        :return: none
        """
        self._download_pics(self.photo_urls)
        self._download_pics(self.instagram_urls, 'instagram')
        self._download_videos()

    def _download_pics(self, urls, file_suffix=''):
        index = 0
        for photo in urls:
            response = requests.get(photo, stream=True)
            if response.status_code == 200:
                with open(os.path.join(DOWNLOAD_FOLDER, 'images', '{}_{}_{}.jpg'.format(self.id, file_suffix, index)), 'wb') as f:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, f)
                index += 1

    def _download_videos(self):
        index = 0
        for video in self.video_urls:
            r = requests.get(video, stream=True)
            f = open(os.path.join(DOWNLOAD_FOLDER, 'videos', '{}_{}.mp4'.format(self.id, index)), 'wb')
            for chunk in r.iter_content(chunk_size=255):
                if chunk:
                    f.write(chunk)
            f.close()
            index += 1


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
        """
        Get recommendations matches from tinder. Its always between 10 and 20 recommendations
        :exception: SystemError --> Tinder has some problems
        :exception: ValueError: --> unknown error. Look at the json output.
        :exception: ConnectionRefusedError --> You are temp banned :D Just wait some time.
        :return: dict of recommendations
        """
        # GET Recs
        response_recs = get_request('/user/recs', token=self.token)
        # Smth went wrong
        if response_recs.status_code != 200:
            if response_recs.status_code == 500:
                # Tinder has some trouble
                raise SystemError('Tinder has some trouble right now! Don´t worry try it later again!')
            else:
                # Unknown Error
                raise ValueError('Cant get Recommandation. {}'.format(response_recs.json()))
        else:
            # create json
            response_recs = response_recs.json()
            # Error?
            if 'message' in response_recs and 'recs timeout' in response_recs['message']:
                raise ConnectionRefusedError('Timeout because too much Rec-requests!')

            # GET result dict
            results = response_recs['results']
            recs = []

            # Create Recommendation objects
            for result in results:
                user = result['user']
                photo_urls = []
                video_urls = []
                instagram_urls = []
                # GET Video or Photo URLs (only high resolution)
                for photo in user['photos']:
                    if 'processedVideos' in photo:
                        video_urls.append(photo['processedVideos'][0]['url'])
                    else:
                        photo_urls.append(photo['url'])
                # GET instagram photo URLs
                if 'instagram' in user and 'photos' in user['instagram']:
                    for insta_photo in user['instagram']['photos']:
                        instagram_urls.append(insta_photo['image'])
                # CREATE Recommendation object
                recs.append(Recommendation(
                    id=user['_id'],
                    distance_mi=user['distance_mi'],
                    name=user['name'],
                    bio=user['bio'],
                    birth_date=get_datetime(user['birth_date']),
                    photo_urls=photo_urls,
                    instagram_urls=instagram_urls,
                    video_urls=video_urls,
                    gender=user['gender'],
                    token=self.token
                ))
            return recs

    def change_location(self, lat: float, lon: float):
        """
        Change location of tinder account.
        :param lat: float
        :param lon: float
        :return: none
        """
        _ = post_request('/user/ping', data={'lat': lat, 'lon': lon}, token=self.token)
        logger.info("Changed Location to {}".format(self.travel_pos.get_location_name()))

    def get_last_activities(self, time_delta_days: int = 30):
        """
        Get last activities like matches. Time
        :param time_delta_days --> Time delta in days for last activities, default 30 (1 month)
        :return: dict with updates
        """
        dt = datetime.now() - timedelta(days=time_delta_days)
        dt_str = dt.strftime('%Y-%m-%dT%H:00:00.404Z')
        return post_request(
            '/updates',
            data={'last_activity_date': dt_str, 'nudge': True},
            token=self.token,
            json=True
        )

    def refresh(self):
        # TODO: do it!
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
