from typing import Any

from werkzeug.exceptions import HTTPException


def handle_exception(error: Exception) -> tuple[dict[str, Any], int]:
    if isinstance(error, HTTPException):
        error_code = error.code if error.code else 500
        return {"message": error.description}, error_code

    return {"message": str(error)}, 500
