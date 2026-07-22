from flask import Blueprint, Response, jsonify, make_response, render_template, request
from loguru import logger

from apps.celery_app.tasks.download import download_task
from config import app_settings
from services.download.helpers.task import get_task_result

download_bp = Blueprint(
    name="download",
    import_name=__name__,
    url_prefix="/download",
    template_folder="templates",
)


@download_bp.get("/")
def home() -> Response:
    return make_response(render_template("download.html", version=app_settings.version))


@download_bp.post("/")
def launch() -> Response:
    data = request.get_json()
    if not (urls := data.get("urls")):
        return make_response(jsonify({"message": "URLs cannot be empty"}), 400)
    if not isinstance(urls, list):
        return make_response(jsonify({"message": "URLs must be a list"}), 400)

    type_dl = data.get("type_dl")
    tasks_uuids = [download_task.delay(url=url, type_dl=type_dl) for url in urls]
    logger.info(f"Tasks UUIDs: {','.join(tasks_uuids)}")

    return make_response(jsonify({"uuids": tasks_uuids}))


@download_bp.get("/<uuid>")
def status(uuid: str) -> Response:
    download = get_task_result(task_id=uuid)

    return make_response(jsonify(download))
