import os

from loguru import logger

bind = "0.0.0.0:8000"
forwarded_allow_ips = "*"
workers = 4
# int(os.getenv("CONCURRENCY")) if os.getenv("CONCURRENCY") else (multiprocessing.cpu_count() + 1)
# Enable workers count regarding cpu

accesslog = "-"
errorlog = "-"


def pre_fork(_, worker):
    """Set GUNICORN_WORKER_ID environment variable before forking workers."""
    os.environ["GUNICORN_WORKER_ID"] = str(worker.age)
    logger.info("GUNICORN_WORKER_ID environment variable set")
