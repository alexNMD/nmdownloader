import platform

from flask import Blueprint, jsonify, Response

from nmdownloader.config import app_settings

hello_bp = Blueprint("hello", __name__)


@hello_bp.get("/")
def hello() -> Response:
    return jsonify(
        {
            "Hello": "World",
            "system": platform.system(),
            "MEDIA_PATH": str(app_settings.media_path),
            "commande_prefix": app_settings.discord.command_prefix,
            "refresh_rate": app_settings.discord.refresh_rate,
            "concurrency": app_settings.celery.concurrency,
        }
    )
