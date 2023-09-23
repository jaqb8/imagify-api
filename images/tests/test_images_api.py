from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from images.models import Image
from rest_framework.test import APIClient
from rest_framework import status
import tempfile
from PIL import Image as PILImage
import factory
from django.db.models import signals
import shutil
from django.core.files.storage import default_storage


IMAGES_URL = reverse("images:images-list")
UPLOAD_IMAGE_URL = reverse("images:image-upload")

generate_expiring_link_url = lambda image_id: reverse(
    "images:generate-link", args=[image_id]
)


@factory.django.mute_signals(signals.pre_save, signals.post_save)
def sample_image(user, **kwargs):
    """Create and return a sample image object (disabled signals in order to avoid creating actual thumbnails)"""
    defaults = {
        "original_file": SimpleUploadedFile(
            "test.jpg", b"file_content", content_type="image/jpeg"
        ),
        "thumbnail_200": SimpleUploadedFile(
            "test.jpg", b"file_content", content_type="image/jpeg"
        ),
        "thumbnail_400": SimpleUploadedFile(
            "test.jpg", b"file_content", content_type="image/jpeg"
        ),
    }
    defaults.update(kwargs)
    return Image.objects.create(user=user, **defaults)


class PublicImagesApiTests(TestCase):
    """Test publicly available images API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving images"""
        res = self.client.get(IMAGES_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class BasicUserImagesApiTests(TestCase):
    """Test basic user images API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@test.com", password="testpass"
        )
        basic_tier_group = Group.objects.get(name="BasicTierUsers")
        basic_tier_group.user_set.add(self.user)
        self.client.force_authenticate(self.user)

    def tearDown(self):
        """Remove media files after each test"""
        path = default_storage.path(f"./{self.user.id}")
        if default_storage.exists(path):
            shutil.rmtree(path)

    def test_retrieve_images(self):
        """Test retrieving images. Output should contain only 200px thumbnail."""

        image = sample_image(user=self.user)

        res = self.client.get(IMAGES_URL)
        image.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

        self.assertTrue(res.data[0].get("thumbnail_200"))
        self.assertIn(image.thumbnail_200.url, res.data[0].get("thumbnail_200"))

        self.assertFalse(res.data[0].get("thumbnail_400"))
        self.assertFalse(res.data[0].get("original_file"))

    def test_upload_image(self):
        """Test uploading an image. Output should contain only 200px thumbnail."""

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = PILImage.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                UPLOAD_IMAGE_URL, {"original_file": ntf}, format="multipart"
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        image = Image.objects.get(id=res.data.get("id"))
        self.assertTrue(res.data.get("thumbnail_200"))
        self.assertIn(image.thumbnail_200.url, res.data.get("thumbnail_200"))

        self.assertFalse(res.data.get("thumbnail_400"))
        self.assertFalse(res.data.get("original_file"))

        self.assertTrue(default_storage.exists(image.original_file.path))

    def test_upload_image_invalid(self):
        """Test uploading an invalid image with Basic Tier"""
        res = self.client.post(
            UPLOAD_IMAGE_URL, {"original_file": "notimage"}, format="multipart"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_generate_expiring_link(self):
        """Test generating an expiring link with Basic Tier"""

        image = sample_image(user=self.user)
        url = generate_expiring_link_url(image.id)

        res = self.client.post(url, {"expires_in": 60})

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PremiumUserImagesApiTests(TestCase):
    """Test premium user images API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@test.com", password="testpass"
        )
        premium_tier_group = Group.objects.get(name="PremiumTierUsers")
        premium_tier_group.user_set.add(self.user)
        self.client.force_authenticate(self.user)

    def tearDown(self):
        """Remove media files after each test"""
        path = default_storage.path(f"./{self.user.id}")
        if default_storage.exists(path):
            shutil.rmtree(path)

    def test_retrieve_images(self):
        """Test retrieving images. Output should contain 200px and 400px thumbnails."""

        image = sample_image(user=self.user)

        res = self.client.get(IMAGES_URL)
        image.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

        self.assertTrue(res.data[0].get("thumbnail_200"))
        self.assertIn(image.thumbnail_200.url, res.data[0].get("thumbnail_200"))

        self.assertTrue(res.data[0].get("thumbnail_400"))
        self.assertIn(image.thumbnail_400.url, res.data[0].get("thumbnail_400"))

        self.assertFalse(res.data[0].get("original_file"))

    def test_upload_image(self):
        """Test uploading an image. Output should contain 200px and 400px thumbnails."""

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = PILImage.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                UPLOAD_IMAGE_URL, {"original_file": ntf}, format="multipart"
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        image = Image.objects.get(id=res.data.get("id"))

        self.assertTrue(res.data.get("thumbnail_200"))
        self.assertIn(image.thumbnail_200.url, res.data.get("thumbnail_200"))

        self.assertTrue(res.data.get("thumbnail_400"))
        self.assertIn(image.thumbnail_400.url, res.data.get("thumbnail_400"))

        self.assertFalse(res.data.get("original_file"))

        self.assertTrue(default_storage.exists(image.original_file.path))

    def test_upload_image_invalid(self):
        """Test uploading an invalid image with Premium Tier"""
        res = self.client.post(
            UPLOAD_IMAGE_URL, {"original_file": "notimage"}, format="multipart"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_generate_expiring_link(self):
        """Test generating an expiring link with Premium Tier"""

        image = sample_image(user=self.user)
        url = generate_expiring_link_url(image.id)

        res = self.client.post(url, {"expires_in": 60})

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
