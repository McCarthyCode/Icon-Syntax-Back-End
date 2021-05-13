from rest_framework.permissions import BasePermission


class IsVerified(BasePermission):
    """
    Allows access only to verified users.
    """
    def has_permission(self, request, view):
        """
        Method returning a Boolean of whether a user exists within a request, and that user has verified their email.
        """
        return bool(request.user and request.user.is_verified)
