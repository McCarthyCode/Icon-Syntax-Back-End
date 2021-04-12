from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..serializers import *

from rest_framework.exceptions import AuthenticationFailed, ValidationError


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
        except ValidationError as e:
            return Response(
                {
                    'errors': ['The credentials used to login were invalid.'],
                    **e.detail,
                },
                status=status.HTTP_400_BAD_REQUEST)
        except AuthenticationFailed as e:
            return Response(
                {'errors': [str(e)]}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(GenericAPIView):
    """
    View for taking in a user's access token and logging them out.
    """
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        POST method for taking a token from a request body, checking if it is valid, and logging out the user if valid, or returning an error response if invalid.
        """
        auth = request.META.get('HTTP_AUTHORIZATION', '').split(' ')

        try:
            assert len(auth) == 2
            assert auth[0] == 'Bearer'
        except AssertionError:
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(data={'access': auth[1]})

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response(
                {
                    'errors': [
                        'The token used to logout was invalid. You may have successfully logged out already.'
                    ],
                    **e.detail,
                },
                status=status.HTTP_400_BAD_REQUEST)

        body = serializer.save()

        return Response(body, status=status.HTTP_205_RESET_CONTENT)