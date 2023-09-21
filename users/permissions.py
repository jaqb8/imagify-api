from rest_framework import permissions
from .models import UserProfile


class IsBasicUser(permissions.IsAuthenticated):
    """
    Custom permission to only allow access to Basic tier users.
    """

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return request.user.userprofile.tier == UserProfile.Tier.BASIC
        return False


class IsPremiumUser(permissions.IsAuthenticated):
    """
    Custom permission to only allow access to Premium tier users.
    """

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return request.user.userprofile.tier == UserProfile.Tier.PREMIUM
        return False


class IsEnterpriseUser(permissions.IsAuthenticated):
    """
    Custom permission to only allow access to Enterprise tier users.
    """

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return request.user.userprofile.tier == UserProfile.Tier.ENTERPRISE
        return False
