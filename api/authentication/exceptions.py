from rest_framework import status
from rest_framework.exceptions import ValidationError


class ConflictError(ValidationError):
    """
    Exception to be used with the HTTP 409 CONFLICT status code. Inherits from rest_framework.exceptions.ValidationError.
    """
    status_code = status.HTTP_409_CONFLICT


class GoneError(ValidationError):
    """
    Exception to be used with the HTTP 410 GONE status code. Inherits from rest_framework.exceptions.ValidationError.
    """
    status_code = status.HTTP_410_GONE
