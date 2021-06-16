from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler as exc_handler

from api import NON_FIELD_ERRORS_KEY


def exception_handler(exc, context):
    response = exc_handler(exc, context)

    if response is not None and 'detail' in response.data:
        detail = response.data['detail']

        # Some DRF messages are missing trailing periods.
        if not detail[-1] in '.?!':
            detail += '.'

        response.data = {NON_FIELD_ERRORS_KEY: [detail]}

    return response


class ConflictError(ValidationError):
    """
    Exception to be used with the HTTP 409 CONFLICT status code. Inherits from rest_framework.exceptions.ValidationError.
    """
    status_code = status.HTTP_409_CONFLICT
