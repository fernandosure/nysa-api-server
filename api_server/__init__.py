from flask import Flask
from flask_cors import CORS
from flask_jsonschema import JsonSchema
from encoders import CustomJSONEncoder
from config import config
import boto3

jsonschema = JsonSchema()
s3 = boto3.resource('s3')


def create_app(config_name):
    app = Flask(__name__)
    app.json_encoder = CustomJSONEncoder
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    CORS(app)
    jsonschema.init_app(app)

    from api_server.api import api as api_blueprint
    from api_server.control_plane import control_plane as control_plane_blueprint
    from api_server.main import main as main_blueprint

    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(control_plane_blueprint, url_prefix='/cp')
    app.register_blueprint(main_blueprint, url_prefix='/')

    return app

