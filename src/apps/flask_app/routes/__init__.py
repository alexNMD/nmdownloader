"""Routes"""

from .download import download_bp
from .health import health_bp
from .hello import hello_bp


def register_routes(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(download_bp)
    app.register_blueprint(hello_bp)
