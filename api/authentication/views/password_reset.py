from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed, NotAuthenticated, PermissionDenied, ValidationError)
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.authentication import NON_FIELD_ERRORS_KEY

from ..permissions import IsVerified
from ..serializers import PasswordResetSerializer


class PasswordResetView(GenericAPIView):
    """
    First step in the process of resetting a password when the original one is known.
    """
    serializer_class = PasswordResetSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method.lower() == 'post':
            permission_classes = [IsAuthenticated & IsVerified]
        else:
            permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]

    def initial(self, request, *args, **kwargs):
        """
        This method overrides the default APIView method so exceptions can be handled.
        """
        try:
            super().initial(request, *args, **kwargs)
        except PermissionDenied as exc:
            detail = exc.detail

            raise PermissionDenied(
                {NON_FIELD_ERRORS_KEY: [detail]}, detail.code)
        except NotAuthenticated as exc:
            detail = exc.detail

            raise NotAuthenticated(
                {NON_FIELD_ERRORS_KEY: [detail]}, detail.code)

    def post(self, request):
        """
        POST method responsible for collecting new and existing passwords (in addition to an Authorization header) and generating a response.
        """
        serializer = self.serializer_class(
            data=request.data, context={'request': request})

        try:
            serializer.is_valid(raise_exception=True)
        except (AuthenticationFailed, ValidationError) as exc:
            return Response(exc.detail, exc.status_code)

        return Response(
            {
                'success': _('Your password has been reset successfully.'),
                'credentials': serializer.save()
            }, status.HTTP_202_ACCEPTED)
