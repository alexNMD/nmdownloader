from flask import request, Blueprint, jsonify, render_template
from loguru import logger

from config import app_settings
from services.download.helpers.task import get_task_result
from apps.celery_app.tasks.download import download_task

download_bp = Blueprint(
    name="download",
    import_name=__name__,
    url_prefix="/download",
    template_folder="templates",
)


@download_bp.get("/")
def home():
    return render_template("download.html", version=app_settings.version)


@download_bp.post("/")
def launch():
    data = request.get_json()
    if not (urls := data.get("urls")):
        return {"message": "URLs cannot be empty"}, 400
    if not isinstance(urls, list):
        return {"message": "URLs must be a list"}, 400

    type_dl = data.get("type_dl")
    tasks_uuids = []
    for url in urls:
        task = download_task.delay(url=url, type_dl=type_dl)
        tasks_uuids.append(task.id)
        logger.info(f"Task sent: {task.id}")

    return jsonify({"uuids": tasks_uuids})


@download_bp.get("/<uuid>")
def status(uuid):
    download = get_task_result(task_id=uuid)

    return jsonify(download)
