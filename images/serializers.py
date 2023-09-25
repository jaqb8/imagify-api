from rest_framework import serializers
from .aws import generate_thumbnail_url
from .models import ExpiringLink, Image
import os
from django.conf import settings
from lib.shared import UserGroupPermissions
from django.core.exceptions import PermissionDenied


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
            raise PermissionDenied("User not authenticated")

        self.user = request.user
        self.user.all_permissions = UserGroupPermissions.get_user_permissions(
            request.user
        )

        if self.user.all_permissions.contains("can_access_original_image"):
            self.fields["original_file"].write_only = False

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        for permission in self.user.all_permissions.startswith("thumbnail:"):
            perm_data = permission.codename.split(":")
            if len(perm_data) < 2:
                raise ValueError(f"Invalid permission codename: {permission.codename}")

            _, height = perm_data
            s3_object_key = os.path.join(
                settings.PUBLIC_MEDIA_LOCATION, instance.original_file.name
            )
            representation[f"thumbnail_{height}"] = generate_thumbnail_url(
                s3_object_key, height
            )

        return representation


class ExpiringLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpiringLink
        exclude = ("image",)
