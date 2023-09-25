from rest_framework import serializers
from .aws import generate_thumbnail_url
from .models import ExpiringLink, Image
import os
from django.conf import settings


class ImageSerializer(serializers.ModelSerializer):
    original_file = serializers.ImageField(write_only=True)

    class Meta:
        model = Image
        fields = (
            "id",
            "uploaded_at",
            "original_file",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if not request and not request.user:
            return

        if request.user.has_perm("images.can_access_original_image"):
            self.fields["original_file"].write_only = False

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        request = self.context.get("request")
        if not request and not request.user:
            return representation

        thumbnail_permissions = request.user.user_permissions.filter(
            codename__startswith="thumbnail:"
        )

        for permission in thumbnail_permissions:
            perm_data = permission.codename.split(":")
            if len(perm_data) < 2:
                raise ValueError(f"Invalid permission codename: {permission.codename}")

            _, height = perm_data
            s3_object_key = os.path.join(
                settings.PUBLIC_MEDIA_LOCATION, instance.original_file.name
            )
            print("media location", settings.PUBLIC_MEDIA_LOCATION)
            print("filename", instance.original_file.name)
            print("s3 key", s3_object_key)
            representation[f"thumbnail_{height}"] = generate_thumbnail_url(
                s3_object_key, height
            )

        return representation


class ExpiringLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpiringLink
        exclude = ("image",)
