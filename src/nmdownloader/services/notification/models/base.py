import http
from typing import Any

import requests
from loguru import logger

from ..helpers.constants import HttpVerb
from ..helpers.exceptions import NotificationError


class BaseNotification:
    TIMEOUT: int = 10
    BASE_URL: str
    API_VERSION: str | None = None
    BEARER_SCHEMA: str = "Bearer"
    API_TOKEN: str | None = None

    @classmethod
    def _call_and_get_json(cls, method: HttpVerb, endpoint: str, **kwargs) -> dict[str, Any]:
        if not cls.API_TOKEN:
            raise NotificationError(f"Auth for {cls.__class__.__name__} not set. Unable to use api.")

        authorization = f"{cls.BEARER_SCHEMA} {cls.API_TOKEN}"
        url = f"{cls.BASE_URL}/{cls.API_VERSION}/{endpoint}" if cls.API_VERSION else f"{cls.BASE_URL}/{endpoint}"
        headers = {"Authorization": authorization, "Content-Type": "application/json"}

        try:
            response = requests.request(method=method, url=url, headers=headers, timeout=cls.TIMEOUT, **kwargs)
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
