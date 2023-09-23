from rest_framework import permissions


class HasExpiringLinkPermission(permissions.IsAuthenticated):
    """Custom permission to check if user has permission to generate expiring link"""

    required_permission = "images.can_generate_expiring_link"

    def has_permission(self, request, view):
        return request.user.has_perm(self.required_permission)
