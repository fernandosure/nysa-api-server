from flask import Flask
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

    jsonschema.init_app(app)

    from api_server.api import api as api_blueprint
    app.register_blueprint(api_blueprint)
    
    return app

