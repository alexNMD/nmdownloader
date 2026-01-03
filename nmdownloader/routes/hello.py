from flask import Blueprint, jsonify, Response


from nmdownloader.config import app_settings

hello_bp = Blueprint("hello", __name__)


@hello_bp.get("/")
def hello() -> Response:
    return jsonify(
        {
            "Hello": "World",
            "LOG_LEVEL": app_settings.log_level,
            "MEDIA_PATH": str(app_settings.media_path),
        }
    )
