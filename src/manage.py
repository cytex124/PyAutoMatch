import logging
import logging.config
import click
from time import sleep

logging.config.fileConfig('logging.ini')

from core.auth import auth_with_facebook_on_tinder
from core.models import TinderCounter

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
def train():
    from core.web import start_ws
    start_ws()


@cli.command()
def createmodel():
    # TODO: Create model command to create AI model of traindata + test
    pass


@cli.command()
@click.option('--notrans', default=False, help='Filters Trans peoples')
@click.option('--savepics', default=False, help='Download the pics of the liked person.')
def run(no_trans, save_pics):
    user = auth_with_facebook_on_tinder()
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
                rec.decide_match(no_trans, save_pics)
            logger.info(TinderCounter())


@cli.command()
def stats():
    from core.dash import run_dash_server
    run_dash_server()


@cli.command()
def ustats():
    from core.db import update_tinder_matches_stats
    user = auth_with_facebook_on_tinder()
    update_tinder_matches_stats(user)


if __name__ == '__main__':
    cli()
