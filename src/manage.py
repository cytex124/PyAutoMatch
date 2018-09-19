import logging
import logging.config
import argparse
from time import sleep

logging.config.fileConfig('logging.ini')

from core.auth import auth
from core.models import TinderCounter
from core.web import start_ws

logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser(description='AutoMatch Tinder')
parser.add_argument('action', help='The action to take (e.g. run, train, cmodel)')


def train():
    start_ws()


def cmodel():
    pass


def run():
    user = auth()
    while 1:
        try:
            recs = user.get_match_recommendations()
        except (ValueError, ConnectionRefusedError) as err:
                logger.warning('waiting 5min...')
                logger.warning(err)
                sleep(300)
        else:
            for rec in recs:
                rec.decide_match()
            counter = TinderCounter()
            logger.info(counter)


if __name__ == '__main__':
    args = parser.parse_args()
    if args.action == 'run':
        run()
    elif args.action == 'train':
        train()
    elif args.action == 'cmodel':
        cmodel()
