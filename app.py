import os
import click
from api_server import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.cli.command()
@click.option("-h", "--host",    default="0.0.0.0")
@click.option("-p", "--port",    type=click.INT, default=5000)
@click.option('-w', '--workers', type=click.INT, default=2)
@click.option('-t', '--timeout', type=click.INT, default=90)
def gunicorn(host, port, workers, timeout):
    """Start the Server with Gunicorn"""
    from gunicorn.app.base import Application

    class FlaskApplication(Application):
        def init(self, parser, opts, args):
            return {
                'bind': '{0}:{1}'.format(host, port),
                'workers': workers, 'timeout': timeout

            }

        def load(self):
            return app

    application = FlaskApplication()
    return application.run()


@app.cli.command()
@click.option("--length", default=25)
@click.option("--profile_dir", default=None)
def profile(length, profile_dir):
    """Start de application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run()


if __name__ == '__main__':
    app.run()
