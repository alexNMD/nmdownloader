from config import app_settings

bind = f"0.0.0.0:{app_settings.gunicorn.port}"
workers = app_settings.gunicorn.workers_count
loglevel = app_settings.nmd_log_level.lower()
accesslog = "-"
