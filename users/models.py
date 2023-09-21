from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    class Tier(models.TextChoices):
        BASIC = "Basic", _("Basic")
        PREMIUM = "Premium", _("Premium")
        ENTERPRISE = "Enterprise", _("Enterprise")

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tier = models.CharField(max_length=20, choices=Tier.choices, default=Tier.BASIC)
