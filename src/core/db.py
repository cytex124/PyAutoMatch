from pony.orm import *
from datetime import datetime
import os
import logging


logger = logging.getLogger(__name__)
db = Database()
db.bind(provider='sqlite', filename=os.path.join('..', 'tinder.sqlite'), create_db=True)


class Person(db.Entity):
    tinder_id = Required(str)
    name = Required(str)
    city = Required(str)
    country = Required(str)
    gender = Required(int)
    birth_date = Required(datetime)
    is_matched = Required(bool)
    has_liked = Required(bool)
    create_time = Required(datetime)


db.generate_mapping(check_tables=True, create_tables=True)


@db_session
def update_tinder_matches_stats(user):
    content = user.get_last_activities()
    for match in content['matches']:
        if 'is_new_message' in match and match['is_new_message']:
            person_tinder_id = match['messages'][0]['from']
        elif 'person' in match:
            person_tinder_id = match['person']['_id']
        else:
            continue
        person_obj = Person.select(lambda p: p.tinder_id == person_tinder_id)[:]
        if person_obj:
            person_obj = person_obj[0]
            person_obj.is_matched = True
            logger.info('Update Person {} from {}, {}'.format(person_obj.name, person_obj.city, person_obj.country))
            commit()
