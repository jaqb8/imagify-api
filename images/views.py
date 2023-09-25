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
    """A base view class for handling image-related operations."""

    permission_classes = [IsAuthenticated]
    serializer_class = ImageSerializer
    renderer_classes = [NonNullJSONRenderer, BrowsableAPIRenderer]


class ImageUploadView(BaseImageView, generics.CreateAPIView):
    """A view for handling image upload requests."""

    queryset = Image.objects.all()

    def perform_create(self, serializer):
        """Saves the uploaded image with the requesting user as the owner."""
        serializer.save(user=self.request.user)


class UserImagesView(BaseImageView, generics.ListAPIView):
    """Saves the uploaded image with the requesting user as the owner."""

    def get_queryset(self):
        """Filters the Image queryset to return only images owned by the requesting user.

        Returns:
            QuerySet: A queryset of Image objects owned by the requesting user.
        """
        return Image.objects.filter(user=self.request.user)


class GenerateExpiringLinkView(generics.CreateAPIView):
    """
    API view that generates an expiring link for an image.

    The view expects a POST request with a JSON payload containing the following fields:
    - `expires_in`: the number of seconds until the link should expire

    The response will be a JSON object with a `url` field containing the generated link.

    If the request is not authenticated or the user does not have the `generate_expiring_link` permission
    for the image, a 403 Forbidden response will be returned.
    """

    queryset = ExpiringLink.objects.all()
    serializer_class = ExpiringLinkSerializer
    permission_classes = [HasExpiringLinkPermission]

    def create(self, request, *args, **kwargs):
        """Handles the creation of an expiring link.

        Overrides the create method to handle the creation of an expiring link, and if successful, generates a URL for the expiring link, returning it in the response data.

        Returns:
            Response: The HTTP response object.
        """

        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            alias = response.data.get("alias")
            url = reverse("images:image-link", kwargs={"alias": alias}, request=request)
            return Response({"url": url}, status=status.HTTP_201_CREATED)
        return response

    def perform_create(self, serializer):
        """Save the expiring link object to the database and sets the cache.

        The method saves the expiring link object to the database, and sets a cache with a timeout as specified in the request data.
        """

        data = serializer.validated_data
        image = get_object_or_404(Image, id=self.kwargs.get("image_id"))
        obj = serializer.save(image=image)
        cache.set(str(obj.alias), "valid", timeout=data.get("expires_in"))


class ExpiringLinkRedirectView(APIView):
    """API view to handle the redirection to the original image file via an expiring link.

    This view extracts the alias from the URL, checks the cache to see if the link is still valid,
    and either redirects the client to the original image file or responds with a `410 Gone` status if the link has expired.
    """

    def get(self, request, *args, **kwargs):
        """Handles GET requests to redirect to the original image or notify of an expired link.

        Returns:
            FileResponse: A response object with the original image file if the link is valid.
            Response: A response object with a `410 Gone` status if the link has expired.
        """

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
