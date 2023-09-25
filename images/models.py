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
