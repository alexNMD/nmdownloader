from flask import request, Blueprint, jsonify, render_template
from loguru import logger

from nmdownloader.libs.task import get_task_result
from nmdownloader.tasks.download_media import download_media_task

download_bp = Blueprint(
    "download", __name__, url_prefix="/download", template_folder="templates"
)


@download_bp.get("/")
def home():
    return render_template("download.html")


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
        task = download_media_task.delay(url=url, type_dl=type_dl)
        tasks_uuids.append(task.id)
        logger.info(f"Task sent: {task.id}")

    return jsonify({"uuids": tasks_uuids})


@download_bp.get("/<uuid>")
def status(uuid):
    download = get_task_result(task_id=uuid)

    return jsonify(download)
