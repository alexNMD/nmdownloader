from typing import Any, Literal, NoReturn

import requests
from loguru import logger

from ..helpers.exceptions import NotificationError


class BaseNotification:
    TIMEOUT: int = 10
    BASE_URL: str
    API_VERSION: str | None = None
    BEARER_SCHEMA: str = "Bearer"
    API_TOKEN: str | None = None

    @classmethod
    def _call_and_get_json(
        cls, method: Literal["GET", "POST", "PATCH", "DELETE"], endpoint: str, **kwargs
    ) -> dict[str, Any]:
        if not cls.API_TOKEN:
            raise NotificationError(f"Auth for {cls.__name__} not set. Unable to use api.")

        authorization = f"{cls.BEARER_SCHEMA} {cls.API_TOKEN}"
        url = f"{cls.BASE_URL}/{cls.API_VERSION}/{endpoint}" if cls.API_VERSION else f"{cls.BASE_URL}/{endpoint}"
        headers = {"Authorization": authorization, "Content-Type": "application/json"}

        try:
            response = requests.request(method=method, url=url, headers=headers, timeout=cls.TIMEOUT, **kwargs)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            cls._handle_http_error(http_error)
        except requests.exceptions.RequestException as error:
            logger.error(f"Unable to reach {cls.__name__}: {error}")
            raise NotificationError(f"Unable to reach {cls.__name__}: {error}") from error

        return response.json()

    @classmethod
    def _handle_http_error(cls, http_error: requests.exceptions.HTTPError) -> NoReturn:
        response = http_error.response
        status_code = response.status_code if response is not None else None
        error_message = f"Unable to use {cls.__name__}, got: {status_code or 'Unknown error'}"

        logger.error(error_message)

        raise NotificationError(error_message) from http_error
