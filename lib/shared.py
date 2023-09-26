from typing import Any
from django.contrib.auth.models import Permission


class UserGroupPermissions:
    """Helper class for checking user permissions including permissions from groups."""

    def __init__(self, permissions):
        self.permissions = permissions

    @classmethod
    def get_user_permissions(cls, user):
        """Gets all permissions for a user including permissions from groups.

        Args:
            user (User): user object

        Returns:
            Set: set of permission dicts
        """
        user_permissions = user.user_permissions.all()
        group_permissions = Permission.objects.filter(group__user=user)
        all_permissions = set(user_permissions) | set(group_permissions)

        return cls(all_permissions)

    def contains(self, value):
        """Checks if a permission exists in permissions set.

        Args:
            value (str): permission codename

        Returns:
            bool: True if the permission exists, False otherwise
        """
        return any(perm.codename == value for perm in self.permissions)

    def startswith(self, value):
        """Return permissions that start with the given value.

        Args:
            value (str): permission codename prefix

        Returns:
            tuple: permissions that start with the given value
        """
        return (perm for perm in self.permissions if perm.codename.startswith(value))
