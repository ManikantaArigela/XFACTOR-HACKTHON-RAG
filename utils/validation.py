from werkzeug.exceptions import BadRequest


def require_json_fields(payload, *fields):
    if not isinstance(payload, dict):
        raise BadRequest("Request body must be a JSON object")
    missing = [field for field in fields if not str(payload.get(field, "")).strip()]
    if missing:
        raise BadRequest(f"Missing required fields: {', '.join(missing)}")
    return payload


def parse_positive_int(value, default, maximum=100):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(parsed, maximum))
