from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import uuid
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from .shared import generate_expiring_link_url, sample_image
from django.http import FileResponse
import time


class PublicExpiringLinksApiTests(TestCase):
    """Test the publicly accessible expiring links API"""

    def setUp(self):
        self.image = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving expiring links"""
        random_uuid = uuid.uuid4()
        res = self.image.get(generate_expiring_link_url(random_uuid))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateExpiringLinksApiTests(TestCase):
    """Test expiring links API with authorized user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass",
        )
        perm_expiring_link = Permission.objects.get(
            codename="can_generate_expiring_link"
        )
        self.image = sample_image(user=self.user)
        self.user.user_permissions.add(perm_expiring_link)
        self.client.force_authenticate(self.user)

    def test_generate_expiring_link_invalid_image(self):
        """Test generating an expiring link for an invalid image id"""
        random_uuid = uuid.uuid4()
        res = self.client.post(
            generate_expiring_link_url(random_uuid), {"expires_in": 300}
        )

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_generate_expiring_link_invalid_expires_in(self):
        """Test generating an expiring link with an invalid expires_in value"""
        res = self.client.post(
            generate_expiring_link_url(self.image.id), {"expires_in": 0}
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        res = self.client.post(
            generate_expiring_link_url(self.image.id), {"expires_in": 30001}
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_generate_expiring_link(self):
        """Test generating an expiring link for an image"""
        res = self.client.post(
            generate_expiring_link_url(self.image.id), {"expires_in": 300}
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("url", res.data)

        res2 = self.client.get(res.data.get("url"))
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res2, FileResponse)

    def test_if_link_expires(self):
        """Test if the generated link expires"""
        res = self.client.post(
            generate_expiring_link_url(self.image.id), {"expires_in": 30}
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("url", res.data)

        time.sleep(32)

        res2 = self.client.get(res.data.get("url"))
        self.assertEqual(res2.status_code, status.HTTP_410_GONE)
        self.assertEqual(res2.data.get("msg"), "Link has expired")
