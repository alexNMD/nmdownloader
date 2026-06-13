from flask import Flask

from apps.flask_app.helpers.exceptions import handle_exception
from apps.flask_app.routes import register_routes

flask_app = Flask(__name__)

register_routes(flask_app)

flask_app.register_error_handler(Exception, handle_exception)
