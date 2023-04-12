#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate

from models import db, Episode, Guest, Appearance

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return ''

@app.route('/episodes', methods = ['GET'])
def get_episodes():
    episodes = Episode.query.all()
    return make_response([episode.to_dict() for episode in episodes], 200)

@app.route('/episodes/<int:id>', methods = ['GET', 'DELETE'])
def episodes_by_id(id):
    episode = Episode.query.filter_by(id=id).first()
    if not episode:
        return make_response({"error": "404: Episode not found"}, 404)
    elif request.method == 'GET':
        return make_response(episode.to_dict(rules=("guests",)), 200)
    elif request.method == 'DELETE':
        db.session.delete(episode)
        db.session.commit()

        return make_response({}, 204)
    
@app.route('/guests', methods = ['GET'])
def get_guests():
    guests = Guest.query.all()
    return make_response([guest.to_dict() for guest in guests], 200)

@app.route('/appearances', methods = ['POST'])
def new_appearance():
    try:
        new_appearance = Appearance(
            rating = request.get_json()['rating'],
            episode_id = request.get_json()['episode_id'],
            guest_id = request.get_json()['guest_id']
        )
        db.session.add(new_appearance)
        db.session.commit()

        return make_response(
                new_appearance.to_dict(rules=('-episode_id', '-guest_id')),
                201
            )
    except Exception as e:
        return make_response({"errors": "400: Validation error"},400)


if __name__ == '__main__':
    app.run(port=5555, debug=True)