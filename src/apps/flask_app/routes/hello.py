import platform

from flask import Blueprint, jsonify, Response

from config import app_settings

hello_bp = Blueprint(name="hello", import_name=__name__)


@hello_bp.get("/")
def hello() -> Response:
    return jsonify(
        {
            "Hello": "World",
            "app": {
                "version": app_settings.version,
                "system": platform.system(),
                "MEDIA_PATH": str(app_settings.media_path),
            },
            "discord": {
                "commande_prefix": app_settings.discord.command_prefix,
                "refresh_rate": app_settings.discord.refresh_rate,
            },
            "celery": {
                "concurrency": app_settings.celery.concurrency,
            },
            "ffmpeg": app_settings.downloader.youtube.ffmpeg.dict(),
        }
    )
