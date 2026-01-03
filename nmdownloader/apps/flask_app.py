from flask import Flask

from nmdownloader.routes import register_routes

flask_app = Flask(__name__)

register_routes(flask_app)
