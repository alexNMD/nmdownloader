import os

from gunicorn.app.base import Application

from apps.flask_app import flask_app


class GunicornApp(Application):
    def __init__(self, app, config_path: str):
        self.application = app
        self.config_path = config_path
        super().__init__()

    def load_config(self):
        self.load_config_from_file(self.config_path)

    def load(self):
        return self.application


def gunicorn() -> None:
    config_path = os.path.join(os.path.dirname(__file__), "gunicorn_conf.py")
    GunicornApp(flask_app, config_path).run()
