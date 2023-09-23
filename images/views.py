from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.renderers import BrowsableAPIRenderer
from .renderers import NonNullJSONRenderer
from .permissions import HasExpiringLinkPermission
from .models import ExpiringLink, Image
from .serializers import (
    ImageSerializer,
    ExpiringLinkSerializer,
)
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage


class BaseImageView:
    permission_classes = [IsAuthenticated]
    serializer_class = ImageSerializer
    renderer_classes = [NonNullJSONRenderer, BrowsableAPIRenderer]


class ImageUploadView(BaseImageView, generics.CreateAPIView):
    queryset = Image.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserImagesView(BaseImageView, generics.ListAPIView):
    def get_queryset(self):
        return Image.objects.filter(user=self.request.user)


class GenerateExpiringLinkView(generics.CreateAPIView):
    """
    API view that generates an expiring link for an image.

    The view expects a POST request with a JSON payload containing the following fields:
    - `expires_in`: the number of seconds until the link should expire

    The response will be a JSON object with a `url` field containing the generated link.

    If the request is not authenticated or the user does not have the `generate_expiring_link` permission
    for the image, a 403 Forbidden response will be returned.

    If the request is successful, a new `ExpiringLink` object will be created and associated with the image.
    The link will be valid for the specified number of seconds and can be accessed via the `/images/<alias>/` URL.

    Note that the `perform_create` method sets a cache key with the link alias as the key and the string "valid"
    as the value. This can be used to check whether a link is still valid without hitting the database.
    """

    queryset = ExpiringLink.objects.all()
    serializer_class = ExpiringLinkSerializer
    permission_classes = [HasExpiringLinkPermission]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            alias = response.data.get("alias")
            url = reverse("images:image-link", kwargs={"alias": alias}, request=request)
            return Response({"url": url}, status=status.HTTP_201_CREATED)
        return response

    def perform_create(self, serializer):
        data = serializer.validated_data
        image = get_object_or_404(Image, id=self.kwargs.get("image_id"))
        obj = serializer.save(image=image)
        cache.set(str(obj.alias), "valid", timeout=data.get("expires_in"))


class ExpiringLinkRedirectView(APIView):
    def get(self, request, *args, **kwargs):
        alias = self.kwargs.get("alias")
        if cache.get(alias):
            link = get_object_or_404(ExpiringLink, alias=alias)
            image = link.image

            return FileResponse(
                default_storage.open(image.original_file.name),
                content_type="image/jpeg",
            )
        else:
            return Response({"msg": "Link has expired"}, status=status.HTTP_410_GONE)
