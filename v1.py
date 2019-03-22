
from bottle_api import *


def init(app, auth):
    api = Api(app)
    api.add_resource(BottleListApi, '/v1/bottle', resource_class_args=[auth])
    api.add_resource(BottleApi, '/v1/bottle/<int:id>', resource_class_args=[auth])
