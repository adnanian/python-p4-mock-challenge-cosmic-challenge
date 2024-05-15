#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app=app)


@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        scientists = [scientist.to_dict(only=('id', 'name', 'field_of_study')) for scientist in Scientist.query.all()]
        return scientists, 200
    
    def post(self):
        try:
            new_scientist = Scientist(
                name=request.get_json().get('name'),
                field_of_study=request.get_json().get('field_of_study')
            )
            db.session.add(new_scientist)
            db.session.commit()
            return new_scientist.to_dict(), 201
        except Exception as e:
            return {'errors': ["validation errors"]}, 400
        
class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            return scientist.to_dict(), 200
        return {'error': 'Scientist not found'}, 404
    
    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            try:
                for attr in (json := request.get_json()):
                    setattr(scientist, attr, json.get(attr))
                db.session.add(scientist)
                db.session.commit()
                return scientist.to_dict(), 202
            except Exception as e:
                return {"errors": ["validation errors"]}, 400
        return {'error': 'Scientist not found'}, 404
    
    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            db.session.delete(scientist)
            db.session.commit()
            return {}, 204
        return {'error': 'Scientist not found'}, 404
    
class Planets(Resource):
    def get(self):
        planets = [planet.to_dict(rules=('-missions', '-scientists')) for planet in Planet.query.all()]
        return planets, 200
    
class Missions(Resource):
    def post(self):
        try:
            new_mission = Mission(
                name=request.get_json().get('name'),
                scientist_id=request.get_json().get('scientist_id'),
                planet_id=request.get_json().get('planet_id')
            )
            db.session.add(new_mission)
            db.session.commit()
            return new_mission.to_dict(), 201
        except Exception as e:
            return {"errors": ["validation errors"]}, 400

api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistById, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
