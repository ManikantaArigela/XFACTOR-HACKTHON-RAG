from werkzeug.exceptions import BadRequest


def require_json_fields(payload, *fields):
    if not isinstance(payload, dict):
        raise BadRequest("Request body must be a JSON object")
    missing = [
        field for field in fields
        if not isinstance(payload.get(field), str) or not payload[field].strip()
    ]
    if missing:
        raise BadRequest(f"Missing required fields: {', '.join(missing)}")
    return payload


def validate_text_length(value, field, maximum):
    value = value.strip()
    if len(value) > maximum:
        raise BadRequest(f"{field} must be {maximum} characters or fewer")
    return value


def validate_image_path(value):
    if value is None:
        return None
    if not isinstance(value, str) or not value.startswith("/api/upload/"):
        raise BadRequest("image_path must come from the image upload endpoint")
    return value


def parse_positive_int(value, default, maximum=100):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(parsed, maximum))
