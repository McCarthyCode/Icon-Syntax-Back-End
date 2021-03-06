from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed, ErrorDetail, NotAuthenticated, ValidationError)
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from rest_framework_simplejwt.exceptions import InvalidToken

from api.authentication import NON_FIELD_ERRORS_KEY

from ..serializers.login_logout import *


class LoginView(GenericAPIView):
    """
    View for taking in an existing user's credentials and authorizing them if valid or denying access if invalid.
    """
    serializer_class = LoginSerializer

    def post(self, request):
        """
        POST method for taking a token from a query string, checking if it is valid, and logging in the user if valid, or returning an error response if invalid.
        """
        redirect_uri = request.query_params.get('next', '/')

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
                'redirect': redirect_uri,
                'credentials': serializer.validated_data
            },
            status=status.HTTP_303_SEE_OTHER)


class LogoutView(GenericAPIView):
    """
    View for taking in a user's access token and logging them out.
    """
    serializer_class = LogoutSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method.lower() == 'post':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]

    def post(self, request):
        """
        POST method for taking a token from a request body, checking if it is valid, and logging out the user if valid, or returning an error response if invalid.
        """
        access = request.META.get('HTTP_AUTHORIZATION', '')
        serializer = self.serializer_class(
            data={'access': access}, context={'user': request.user})

        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed as exc:
            return Response(
                {NON_FIELD_ERRORS_KEY: [exc.detail]}, exc.status_code)

        return Response(
            {'success': str(_('You have successfully logged out.'))},
            status.HTTP_205_RESET_CONTENT)
