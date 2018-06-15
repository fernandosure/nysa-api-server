from flask import Blueprint

api = Blueprint('api', __name__)

from api_server.api import errors, endpoints
