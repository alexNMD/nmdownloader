from celery.result import AsyncResult

from src.apps.celery_app import celery_app


def get_task_result(task_id: str) -> dict:
    result: AsyncResult = AsyncResult(task_id, app=celery_app)
    info = str(result.info) if isinstance(result.info, Exception) else result.info
    return dict(successful=result.successful(), status=result.status, info=info)
