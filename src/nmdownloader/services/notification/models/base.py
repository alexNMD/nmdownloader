import http
from abc import ABC
from typing import Any

import requests
from loguru import logger

from ..helpers.exceptions import NotificationError


class BaseNotification(ABC):
    TIMEOUT: int = 10
    BASE_URL: str
    API_VERSION: str | None = None
    API_KEY: str | None = None

    @classmethod
    def _call_and_get_json(cls, endpoint: str, **kwargs) -> dict[str, Any]:
        url = f"{cls.BASE_URL}/{cls.API_VERSION}/{endpoint}" if cls.API_VERSION else f"{cls.BASE_URL}/{endpoint}"

        try:
            response = requests.request(url=url, timeout=cls.TIMEOUT, **kwargs)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            if http_error.response.status_code == http.HTTPStatus.UNAUTHORIZED:
                logger.error(f"Auth for {cls.__class__.__name__} invalid. Unable to use api.")
                raise NotificationError from http_error
            logger.error(f"Unable to use {cls.__class__.__name__}, got: {http_error.response.status_code}")
            raise NotificationError from http_error
        except requests.exceptions.RequestException as error:
            logger.error(f"Unable to reach {cls.__class__.__name__}: {error}")
            raise NotificationError from error

        return response.json()
