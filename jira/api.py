from flask_restful import Api, Resource
from flask import Blueprint, abort

bp = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(bp)

class Task1Resource(Resource):
    def get(self, text):
        return text



api.add_resource(Task1Resource, "/echo/<text>")
