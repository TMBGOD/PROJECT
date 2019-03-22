from flask_restful import Resource, Api
from flask_restful import reqparse
from flask import jsonify
from flask import abort
import extra.auth as auth
from models import Bottle
bottle_parser = reqparse.RequestParser()
bottle_parser.add_argument('title', required=True)
bottle_parser.add_argument('content', required=True)


class BottleListApi(Resource):
    def __init__(self, auth):
        super(BottleListApi, self).__init__()
        self._auth = auth

    def get(self):
        bottle = Bottle.query.all()
        return jsonify(bottle=[i.serialize for i in bottle])

    def post(self):
        if not self._auth.is_authorized():
            abort(401)
        args = bottle_parser.parse_args()
        bottle = Bottle.add(args['title'], args['content'], self._auth.get_user())
        return jsonify(bottle.serialize)


class BottleApi(Resource):

    def __init__(self, auth):
        super(BottleApi, self).__init__()
        self._auth = auth

    def get(self, id):
        bottle = Bottle.query.filter_by(id=id).first()
        if not bottle:
            abort(404)
        return jsonify(bottle.serialize)

    def delete(self, id):
        if not self._auth.is_authorized():
            abort(401)
        bottle = Bottle.query.filter_by(id=id).first()
        if bottle.user_id != self._auth.get_user().id:
            abort(403)
        Bottle.delete(bottle)
        return jsonify({"deleted": True})
