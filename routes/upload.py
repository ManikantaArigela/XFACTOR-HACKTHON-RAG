from flask import Blueprint, current_app, request, send_from_directory

from services.storage import LocalImageStorage
from utils.responses import success

upload_bp = Blueprint("upload", __name__)


@upload_bp.post("/upload")
def upload_image():
    storage = LocalImageStorage(
        current_app.config["STORAGE_DIR"], current_app.config["ALLOWED_IMAGE_EXTENSIONS"]
    )
    image_path = storage.save(request.files.get("image"))
    return success({"image_path": image_path}, "Image uploaded successfully", 201)


@upload_bp.get("/upload/<path:filename>")
def get_image(filename):
    storage = LocalImageStorage(
        current_app.config["STORAGE_DIR"], current_app.config["ALLOWED_IMAGE_EXTENSIONS"]
    )
    path = storage.path_for(filename)
    if path.suffix.lower().lstrip(".") not in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        from werkzeug.exceptions import BadRequest

        raise BadRequest("Unsupported image type")
    return send_from_directory(storage.root, path.name)
