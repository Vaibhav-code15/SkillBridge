"""Private PDF validation and storage primitives."""

import logging
import ntpath
import uuid
from pathlib import Path

from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation, ValidationError
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from django.utils.text import get_valid_filename

logger = logging.getLogger(__name__)
MAX_RESUME_BYTES = 5 * 1024 * 1024


@deconstructible
class PrivateResumeStorage(FileSystemStorage):
    @property
    def location(self):
        return str(Path(settings.PRIVATE_MEDIA_ROOT).resolve())

    @property
    def base_url(self):
        return None

    def url(self, name):
        raise ValueError("Private resumes are not publicly accessible.")


private_resume_storage = PrivateResumeStorage()


def resume_path(instance, filename):
    return f"resumes/{uuid.uuid4().hex}.pdf"


def display_name(filename):
    basename = ntpath.basename(str(filename).replace("/", "\\"))
    try:
        safe = get_valid_filename(basename)
    except ValueError, SuspiciousFileOperation:
        safe = "resume.pdf"
    return safe[:200] or "resume.pdf"


def validate_pdf(upload):
    if not str(upload.name).lower().endswith(".pdf"):
        raise ValidationError("Choose a PDF file with a .pdf extension.")
    if not upload.size or upload.size > MAX_RESUME_BYTES:
        raise ValidationError("The PDF must be nonempty and no larger than 5 MB.")
    try:
        upload.seek(0)
        header = upload.read(5)
        upload.seek(max(0, upload.size - 1024))
        trailer = upload.read(1024)
        if header != b"%PDF-" or b"%%EOF" not in trailer:
            raise ValidationError(
                "The file is not a valid PDF: its header or end marker is missing."
            )
    finally:
        upload.seek(0)


def delete_private_file(name):
    if not name:
        return
    try:
        private_resume_storage.delete(name)
    except OSError:
        logger.exception("Could not remove an old private resume file")
