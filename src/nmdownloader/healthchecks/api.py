import requests

from nmdownloader.config import app_settings


def main() -> None:
    requests.get(f"http://localhost:{app_settings.gunicorn.port}/health/check").raise_for_status()


if __name__ == "__main__":
    main()
