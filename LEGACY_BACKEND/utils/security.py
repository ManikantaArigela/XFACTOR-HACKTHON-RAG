from functools import wraps
from uuid import UUID

from flask import g, request
from werkzeug.exceptions import BadRequest


def optional_user_id(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        raw_user_id = request.headers.get("X-User-Id")
        if raw_user_id:
            try:
                g.user_id = UUID(raw_user_id)
            except ValueError as error:
                raise BadRequest("X-User-Id must be a valid UUID") from error
        else:
            g.user_id = None
        return view(*args, **kwargs)

    return wrapped
