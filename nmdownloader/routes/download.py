from flask import request, Blueprint, jsonify, Response, abort

from loguru import logger

from nmdownloader.libs.lib_task import get_download_task
from nmdownloader.services.download_handler import DownloadHandler
from nmdownloader.tasks.download_tasks import download_task

download_bp = Blueprint("download", __name__, url_prefix="/download")


@download_bp.post("/")
def launch() -> Response:
    data = request.get_json()
    if not (url := data.get("url")):
        abort(code=400, description="URL cannot be empty")
    type_dl = data.get("type_dl")

    task = download_task.delay(url=url, type_dl=type_dl)
    logger.info(f"Task sent: {task.id}")

    return jsonify(dict(uuid=task.id))


@download_bp.get("/<uuid>")
def status(uuid) -> Response:
    download_meta = get_download_task(uuid, json_readable=True)

    return jsonify(download_meta)


@download_bp.delete("/<uuid>")
def stop(uuid) -> Response:
    download_meta = get_download_task(uuid)
    if not isinstance(download_meta.get("download"), DownloadHandler):
        abort(code=400, description="Unable to retrieve download")

    download_meta["download"].cancel()
    logger.info(f"Task: {uuid} Revoked")

    return jsonify(dict(message="Download stopped"))
