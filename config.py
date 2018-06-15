import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    JSONSCHEMA_DIR = os.path.join(basedir, 'api_server', 'api', 'schemas')
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET') or 'mbo-nysa-api-server'
    AWS_SQS_NOTIFICATION_QUEUE = os.getenv('AWS_SQS_NOTIFICATION_QUEUE') or 'nysa-scheduler-queue'
    SLACK_NOTIFICATIONS_WEBHOOK_URL = os.getenv('SLACK_NOTIFICATIONS_WEBHOOK_URL')

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