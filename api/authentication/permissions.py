from rest_framework import permissions


class IsSafeMethod(permissions.BasePermission):
    """
    Allows access IFF the request method is safe.
    """

    def has_permission(self, request, view):
        """
        Method returning a Boolean of whether the request method is listed as safe.
        """
        return request.method in permissions.SAFE_METHODS


class IsVerified(permissions.BasePermission):
    """
    Allows access only to verified users.
    """

    def has_permission(self, request, view):
        """
        Method returning a Boolean of whether a user exists within a request, and that user has verified their email.
        """
        return not request.user.is_anonymous and (request.user.is_verified \
            or request.user.is_staff or request.user.is_superuser)


class IsOwner(permissions.BasePermission):
    """
    Allows only access to owners, except for safe methods (e.g. GET).
    """

    def has_object_permission(self, request, view, obj):
        """
        Method returning a Boolean of whether a request method is safe, or whether a user exists within a request and that user owns the object.
        """
        return bool(request.user and request.user == obj.owner)
