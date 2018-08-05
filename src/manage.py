import defopt
from core.auth import auth
from core.models import TinderCounter


def run():
    user = auth()
    for _ in range(100):
        recs = user.get_match_recommendations()
        for rec in recs:
            rec.decide_match()
        counter = TinderCounter()
        print(counter)


if __name__ == '__main__':
    defopt.run([run])
