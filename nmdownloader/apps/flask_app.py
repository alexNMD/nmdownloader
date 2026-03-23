from flask import Flask
from werkzeug.exceptions import HTTPException

from nmdownloader.routes import register_routes

flask_app = Flask(__name__, template_folder="../static/templates", static_folder="../static")

register_routes(flask_app)


@flask_app.errorhandler(Exception)
def handle_exception(error: Exception):
    if isinstance(error, HTTPException):
        return {"message": error.description}, error.code

    return {"message": str(error)}, 500
