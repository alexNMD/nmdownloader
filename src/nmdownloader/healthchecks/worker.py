from nmdownloader.apps.celery_app import celery_app


def main() -> None:
    celery_app.control.inspect().ping()


if __name__ == "__main__":
    main()
