from rest_framework import permissions


class IsVerified(permissions.BasePermission):
    """
    Allows access only to verified users.
    """
    def has_permission(self, request, view):
        """
        Method returning a Boolean of whether a user exists within a request, and that user has verified their email.
        """
        return bool(request.user and request.user.is_verified)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allows only access to admin users, except for safe methods (e.g. GET).
    """
    def has_permission(self, request, view):
        """
        Method returning a Boolean of whether a request method is safe, or whether a user exists within a request and that user is staff.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(request.user and request.user.is_staff)
