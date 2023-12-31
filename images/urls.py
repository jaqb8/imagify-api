from django.urls import path
from .views import (
    ExpiringLinkRedirectView,
    GenerateExpiringLinkView,
    ImageUploadView,
    UserImagesView,
)

app_name = "images"

urlpatterns = [
    path("", UserImagesView.as_view(), name="images-list"),
    path("upload/", ImageUploadView.as_view(), name="image-upload"),
    path(
        "generate-link/<uuid:image_id>/",
        GenerateExpiringLinkView.as_view(),
        name="generate-link",
    ),
    path(
        "link/<uuid:alias>/",
        ExpiringLinkRedirectView.as_view(),
        name="image-link",
    ),
]
