from pathlib import Path
from uuid import uuid4

from PIL import Image, UnidentifiedImageError
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename


class LocalImageStorage:
    def __init__(self, root, allowed_extensions):
        self.root = Path(root).resolve()
        self.allowed_extensions = allowed_extensions
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, file: FileStorage):
        if not file or not file.filename:
            raise BadRequest("An image file is required")
        original_name = secure_filename(file.filename)
        extension = Path(original_name).suffix.lower().lstrip(".")
        if not original_name or extension not in self.allowed_extensions:
            raise BadRequest("Unsupported image type")
        try:
            image = Image.open(file.stream)
            image.verify()
            file.stream.seek(0)
        except (UnidentifiedImageError, OSError) as error:
            raise BadRequest("Uploaded file is not a valid image") from error

        stored_name = f"{uuid4().hex}.{extension}"
        destination = (self.root / stored_name).resolve()
        if self.root not in destination.parents:
            raise BadRequest("Invalid image path")
        file.save(destination)
        return f"/api/upload/{stored_name}"

    def path_for(self, filename):
        safe_name = secure_filename(filename)
        destination = (self.root / safe_name).resolve()
        if self.root not in destination.parents:
            raise BadRequest("Invalid image path")
        return destination
