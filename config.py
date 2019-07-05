import os
from secret_manager import get_secret

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    JSONSCHEMA_DIR = os.path.join(basedir, 'api_server', 'api', 'schemas')
    AWS_S3_BUCKET = get_secret('AWS_S3_BUCKET') or 'nysa-api-server'
    AWS_SQS_NOTIFICATION_QUEUE = get_secret('NYSA_SCHEDULER_SQS_QUEUE') or 'nysa-scheduler-queue'
    SLACK_NOTIFICATIONS_WEBHOOK_URL = get_secret('SLACK_NOTIFICATIONS_WEBHOOK_URL')

    #disable SSL
    SSl_DISABLE = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

        # handle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,
    'default': DevelopmentConfig
}