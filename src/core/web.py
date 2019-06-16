from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify
from .auth import auth_with_facebook_on_tinder
from singleton_decorator import singleton
import requests
import os


app = Flask(__name__)
base = os.path.dirname(os.path.abspath(os.path.dirname(os.path.realpath(__file__))))


@singleton
class TinderTrain:

    def __init__(self):
        self.user = auth_with_facebook_on_tinder()
        self.recs = None
        self.recs_counter = 0
        self.last_rec = None

    def next_partner(self):
        if self.recs and len(self.recs) - 1 == self.recs_counter:
            self.recs_counter = 0
            self.recs = None
        if not self.recs:
            self.recs = self.user.get_match_recommendations()
        data = self.recs[self.recs_counter]
        if len(self.recs) - 1 != self.recs_counter:
            self.recs_counter += 1
        self.last_rec = data
        return data


@app.route("/")
def to_home():
    return redirect(url_for('train'))


@app.route("/home")
def train():
    tinder_train = TinderTrain()
    data = tinder_train.next_partner()
    return render_template('train.html', url=data.photo_urls[0], id=data.id)


@app.route("/dislike")
def dislike():
    tinder_train = TinderTrain()
    if tinder_train.last_rec:
        tinder_train.last_rec.dislike()
    return redirect(url_for('train'))


@app.route("/like", methods=['POST'])
def like():
    result = request.values
    file = '{}_{}_{}.jpg'.format(result['id'], result['rating'], result['race'])
    with open(os.path.join(base, 'train_data', file), 'wb') as handle:
        response = requests.get(result['url'], stream=True)
        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)
    tinder_train = TinderTrain()
    tinder_train.last_rec.like()
    partner = tinder_train.next_partner()
    return jsonify({
        'id': partner.id,
        'url': partner.photo_urls[0]
    })


def start_ws():
    app.run()
