import os
from typing import TYPE_CHECKING

from gunicorn.app.base import Application

from apps.flask_app import flask_app

if TYPE_CHECKING:
    from flask import Flask


class GunicornApp(Application):
    def __init__(self, app: Flask, config_path: str) -> None:
        self.application = app
        self.config_path = config_path
        super().__init__()

    def load_config(self) -> None:
        self.load_config_from_file(self.config_path)

    def load(self) -> Flask:
        return self.application


def gunicorn() -> None:
    config_path = os.path.join(os.path.dirname(__file__), "gunicorn_conf.py")
    GunicornApp(flask_app, config_path).run()
