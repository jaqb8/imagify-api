from rest_framework import serializers
from rest_framework.fields import empty
from .models import ExpiringLink, Image


class BaseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("id", "original_file", "uploaded_at")


class BasicTierImageSerializer(BaseImageSerializer):
    class Meta(BaseImageSerializer.Meta):
        fields = ("id", "thumbnail_200", "uploaded_at")


class PremiumTierImageSerializer(BaseImageSerializer):
    class Meta(BaseImageSerializer.Meta):
        fields = ("id", "thumbnail_200", "thumbnail_400", "uploaded_at")


class EnterpriseTierImageSerializer(BaseImageSerializer):
    class Meta(BaseImageSerializer.Meta):
        fields = (
            "id",
            "thumbnail_200",
            "thumbnail_400",
            "original_file",
            "uploaded_at",
        )


class ExpiringLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpiringLink
        exclude = ("image",)
