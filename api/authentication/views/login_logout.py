from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.authentication import NON_FIELD_ERRORS_KEY

from ..serializers import *

from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken


class LoginView(GenericAPIView):
    """
    View for taking in an existing user's credentials and authorizing them if valid or denying access if invalid.
    """
    serializer_class = LoginSerializer

    def post(self, request):
        """
        POST method for taking a token from a query string, checking if it is valid, and logging in the user if valid, or returning an error response if invalid.
        """
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed as exc:
            return Response(
                {NON_FIELD_ERRORS_KEY: [exc.detail]}, status=exc.status_code)

        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(GenericAPIView):
    """
    View for taking in a user's access token and logging them out.
    """
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        """
        This method overrides the default APIView method so exceptions can be handled.
        """
        try:
            super().initial(request, *args, **kwargs)
        except (AuthenticationFailed, InvalidToken) as exc:
            raise AuthenticationFailed(
                {NON_FIELD_ERRORS_KEY: [_('The provided token is invalid.')]},
                'invalid')
        except NotAuthenticated as exc:
            raise NotAuthenticated(
                {
                    NON_FIELD_ERRORS_KEY:
                    [_('Authentication credentials were not provided.')]
                }, 'not_authenticated')


    def post(self, request):
        """
        POST method for taking a token from a request body, checking if it is valid, and logging out the user if valid, or returning an error response if invalid.
        """
        access = request.META.get('HTTP_AUTHORIZATION', '')
        serializer = self.serializer_class(data={'access': access})

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exc:
            return Response(exc.detail, exc.status_code)

        return Response(status=status.HTTP_205_RESET_CONTENT)
