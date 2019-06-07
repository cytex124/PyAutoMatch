import logging
import logging.config
import click
from time import sleep

logging.config.fileConfig('logging.ini')

from core.auth import auth
from core.models import TinderCounter
from core.web import start_ws


logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
def train():
    start_ws()


@cli.command()
def createmodel():
    pass


@cli.command()
@click.option('--notrans', default=False, help='Filters Trans peoples')
@click.option('--savepics', default=False, help='Download the pics of the liked person.')
def run(notrans, savepics):
    user = auth()
    while 1:
        try:
            recs = user.get_match_recommendations()
        except (ValueError, ConnectionRefusedError) as err:
                logger.warning('Temp Ban from tinder because bot was very obviously.')
                logger.warning('waiting 10min...')
                logger.warning(err)
                sleep(600)
        else:
            for rec in recs:
                rec.decide_match(notrans, savepics)
            logger.info(TinderCounter())


if __name__ == '__main__':
    cli()
