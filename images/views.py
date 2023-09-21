from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.reverse import reverse
from users.models import UserProfile
from users.permissions import IsEnterpriseUser
from .models import ExpiringLink, Image
from .serializers import (
    BaseImageSerializer,
    BasicTierImageSerializer,
    EnterpriseTierImageSerializer,
    ExpiringLinkSerializer,
    PremiumTierImageSerializer,
)
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage


class ImageUploadView(generics.CreateAPIView):
    queryset = Image.objects.all()
    serializer_class = BaseImageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserImagesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Image.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        user_tier = self.request.user.userprofile.tier

        if user_tier == UserProfile.Tier.BASIC:
            return BasicTierImageSerializer
        elif user_tier == UserProfile.Tier.PREMIUM:
            return PremiumTierImageSerializer
        else:
            return EnterpriseTierImageSerializer


class GenerateExpiringLinkView(generics.CreateAPIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """

    queryset = ExpiringLink.objects.all()
    serializer_class = ExpiringLinkSerializer
    permission_classes = [IsEnterpriseUser]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            alias = response.data.get("alias")
            url = reverse("image-link", kwargs={"alias": alias}, request=request)
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
