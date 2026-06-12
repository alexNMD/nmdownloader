from werkzeug.exceptions import HTTPException


def handle_exception(error: Exception):
    if isinstance(error, HTTPException):
        return {"message": error.description}, error.code

    return {"message": str(error)}, 500
