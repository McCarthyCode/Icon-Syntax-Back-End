from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException
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


class BadRequestError(APIException):
    """
    Exception to be used with the HTTP 400 BAD REQUEST status code. Inherits from rest_framework.exceptions.APIException.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _(
        'Your browser sent a request that the server could not understand. Please check your input and try again.')
    default_code = 'bad_request'


class ConflictError(APIException):
    """
    Exception to be used with the HTTP 409 CONFLICT status code. Inherits from rest_framework.exceptions.APIException.
    """
    status_code = status.HTTP_409_CONFLICT
    default_detail = _(
        'An entry with some or all of the data provided already exists.')
    default_code = 'conflict'


class InternalServerError(APIException):
    """
    Exception to be used with the HTTP 500 INTERNAL SERVER ERROR status code. Inherits from rest_framework.exceptions.APIException.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('An internal server error occurred.')
    default_code = 'internal_server_error'
