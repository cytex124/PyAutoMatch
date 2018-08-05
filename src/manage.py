import defopt
from core.auth import auth


def run():
    token = auth()
    print(token)


if __name__ == '__main__':
    defopt.run([run])
