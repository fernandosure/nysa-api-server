from api_server.api import api
from ..logger import log
from api_server.exceptions import ValidationError
from flask_jsonschema import ValidationError as JsonSchemaValidationError
from flask import jsonify


@api.app_errorhandler(400)
def bad_request(message):
    log.error('bad request %s', message)
    response = jsonify({'error': 'bad request', 'message': str(message)})
    response.status_code = 400
    return response


@api.app_errorhandler(401)
def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': str(message)})
    response.status_code = 401
    return response


@api.app_errorhandler(403)
def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': str(message)})
    response.status_code = 403
    return response


@api.app_errorhandler(404)
def not_found(e):
    response = jsonify({'error': 'not found'})
    response.status_code = 404
    return response


@api.app_errorhandler(405)
def method_not_allowed(e):
    response = jsonify({'error': 'method not allowed'})
    response.status_code = 405
    return response


@api.app_errorhandler(500)
def internal_server_error(e):
    log.error('internal server error')
    response = jsonify({'error': 'internal server error'})
    response.status_code = 500
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    log.error('Validation Error %s', e)
    response = jsonify({'error': 'validation_error', 'message': e.args[0]})
    response.status_code = 422
    return response


@api.errorhandler(JsonSchemaValidationError)
def schema_validation_error(e):
    log.error('schema_validation_error:{}'.format(e))
    response = jsonify({'error': 'validation_error', 'message': e.args[0]})
    response.status_code = 400
    return response
