import os
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from django.utils import timezone
import uuid


def original_image_path(instance, filename):
    """Generate file path for original image"""

    extension = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    return os.path.join(f"{instance.user.id}/original/", filename)


class Image(models.Model):
    """Model representing an image uploaded by a user.

    This model is designed to store images uploaded by users along with their metadata. It has fields for the image file, the user who uploaded it, and the time of upload. Additionally, it defines permissions regarding who can access the original image and
    its thumbnails of specified sizes.

    Attributes:
        id (UUIDField): A unique identifier for each image record.
        user (ForeignKey): Reference to the user who uploaded the image.
        original_file (ImageField): The uploaded image file.
        uploaded_at (DateTimeField): The time at which the image was uploaded.
    """

    class Meta:
        permissions = [
            ("can_access_original_image", "Can access original image"),
            ("thumbnail:200", "can access 200px thumbnail"),
            ("thumbnail:400", "can access 400px thumbnail"),
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_file = models.ImageField(upload_to=original_image_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def filename(self):
        return self.original_file.name.split("/")[-1]

    def __str__(self):
        return f"Image by {self.user.username} - {self.filename} - {self.uploaded_at}"


class ExpiringLink(models.Model):
    """Model representing an expiring link for an image.

    This model is utilized to generate time-sensitive links for images. Each link is associated with a specific image and has a predetermined lifespan after which it becomes inactive.

    Attributes:
        alias (UUIDField): A unique identifier for each expiring link record.
        image (ForeignKey): Reference to the associated image for this link.
        created_at (DateTimeField): The time at which the expiring link was generated.
        expires_in (IntegerField): The lifespan of the link in seconds.
    """

    class Meta:
        permissions = [
            ("can_generate_expiring_link", "Can generate expiring link"),
        ]

    alias = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_in = models.IntegerField(
        validators=[
            MinValueValidator(30),
            MaxValueValidator(30000),
        ]
    )

    @property
    def is_expired(self):
        return (timezone.now() - self.created_at).seconds > self.expires_in

    def __str__(self):
        return reverse("images:image-link", kwargs={"alias": self.alias})
