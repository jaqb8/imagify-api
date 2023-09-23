from rest_framework import serializers
from .models import ExpiringLink, Image


class ImageSerializer(serializers.ModelSerializer):
    original_file = serializers.ImageField(write_only=True)
    thumbnail_200 = serializers.SerializerMethodField()
    thumbnail_400 = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = (
            "id",
            "uploaded_at",
            "original_file",
            "thumbnail_200",
            "thumbnail_400",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        user = request.user if request else None

        if user and user.has_perm("images.can_access_original_image"):
            self.fields["original_file"].write_only = False

    def get_thumbnail_200(self, obj):
        request = self.context.get("request")
        user = request.user if request else None
        if user.has_perm("images.can_access_200px_thumbnail"):
            return request.build_absolute_uri(obj.thumbnail_200.url)

    def get_thumbnail_400(self, obj):
        request = self.context.get("request")
        user = request.user if request else None
        if user.has_perm("images.can_access_400px_thumbnail"):
            return request.build_absolute_uri(obj.thumbnail_400.url)


class ExpiringLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpiringLink
        exclude = ("image",)
