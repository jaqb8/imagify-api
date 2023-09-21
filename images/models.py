import os
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from django.contrib.sites.models import Site
from django_advance_thumbnail import AdvanceThumbnailField
from django.utils import timezone
import uuid


def original_image_path(instance, filename):
    """Generate file path for original image"""

    extension = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    return os.path.join(f"{instance.user.id}/original/", filename)


def thumbnail_200_path(instance, filename):
    return f"{instance.user.id}/thumbnail_200/{filename}"


def thumbnail_400_path(instance, filename):
    return f"{instance.user.id}/thumbnail_400/{filename}"


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_file = models.ImageField(upload_to=original_image_path)
    thumbnail_200 = AdvanceThumbnailField(
        source_field="original_file", upload_to=thumbnail_200_path, size=(200, 200)
    )
    thumbnail_400 = AdvanceThumbnailField(
        source_field="original_file", upload_to=thumbnail_400_path, size=(400, 400)
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def filename(self):
        return self.original_file.name.split("/")[-1]

    def __str__(self):
        return f"Image by {self.user.username} - {self.uploaded_at}"


class ExpiringLink(models.Model):
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
        relative_url = reverse("image-link", kwargs={"alias": self.alias})
        domain = Site.objects.get_current().domain
        return f"http://{domain}{relative_url}"
