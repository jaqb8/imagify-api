from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from images.models import Image


generate_expiring_link_url = lambda image_id: reverse(
    "images:generate-link", args=[image_id]
)


def sample_image(user, **kwargs):
    """Create and return a sample image object (disabled signals in order to avoid creating actual thumbnails)"""
    defaults = {
        "original_file": SimpleUploadedFile(
            "test.jpg", b"file_content", content_type="image/jpeg"
        )
    }
    defaults.update(kwargs)
    return Image.objects.create(user=user, **defaults)
