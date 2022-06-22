from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed, ErrorDetail, NotAuthenticated, ValidationError)
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from rest_framework_simplejwt.exceptions import InvalidToken

from api.authentication import NON_FIELD_ERRORS_KEY
from api.authentication.permissions import IsSafeMethod

from ..serializers.login_logout import *


class LoginView(GenericAPIView):
    """
    View for taking in an existing user's credentials and authorizing them if valid or denying access if invalid.
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        """
        POST method for taking a token from a query string, checking if it is valid, and logging in the user if valid, or returning an error response if invalid.
        """
        serializer = self.serializer_class(
            data=request.data, context={'user': request.user})

        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed as exc:
            return Response(
                {NON_FIELD_ERRORS_KEY: [exc.detail]}, status=exc.status_code)

        return Response(
            {
                'success': str(_('You have successfully logged in.')),
                'credentials': serializer.validated_data
            },
            status=status.HTTP_200_OK)


class LogoutView(GenericAPIView):
    """
    View for taking in a user's access token and logging them out.
    """

    serializer_class = LogoutSerializer
    permission_classes = [IsSafeMethod | IsAuthenticated]

    def post(self, request):
        """
        POST method for taking a token from a request body, checking if it is valid, and logging out the user if valid, or returning an error response if invalid.
        """
        serializer = self.serializer_class(
            data={}, context={'user': request.user})

        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed as exc:
            return Response(
                {NON_FIELD_ERRORS_KEY: [exc.detail]}, exc.status_code)

        return Response(
            {'success': str(_('You have successfully logged out.'))},
            status.HTTP_205_RESET_CONTENT)
