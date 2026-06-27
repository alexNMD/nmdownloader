from flask import Blueprint, Response, jsonify

health_bp = Blueprint(name="health", import_name=__name__, url_prefix="/health")


@health_bp.get("/check")
def health_check() -> Response:
    return jsonify({"status": "ok"})
