from typing import Any

from celery.result import AsyncResult

from nmdownloader.apps import celery_app


def get_task_result(task_id: str) -> dict[str, Any]:
    result = AsyncResult(task_id, app=celery_app)
    info = str(result.info) if isinstance(result.info, Exception) else result.info
    return dict(successful=result.successful(), status=result.status, info=info)
