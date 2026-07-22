"""Routes"""

from typing import TYPE_CHECKING

from .download import download_bp
from .health import health_bp
from .hello import hello_bp

if TYPE_CHECKING:
    from flask import Flask


def register_routes(app: Flask) -> None:
    app.register_blueprint(health_bp)
    app.register_blueprint(download_bp)
    app.register_blueprint(hello_bp)
