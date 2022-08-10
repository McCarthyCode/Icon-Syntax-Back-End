from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed, NotAuthenticated, PermissionDenied, ValidationError)
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.authentication import NON_FIELD_ERRORS_KEY

from ..permissions import IsSafeMethod, IsVerified
from ..serializers import PasswordResetSerializer


class PasswordResetView(GenericAPIView):
    """
    First step in the process of resetting a password when the original one is known.
    """
    serializer_class = PasswordResetSerializer
    permission_classes = [IsSafeMethod | (IsAuthenticated & IsVerified)]

    def post(self, request):
        """
        POST method responsible for collecting new and existing passwords (in addition to an Authorization header) and generating a response.
        """
        serializer = self.serializer_class(
            data=request.data, context={'user': request.user})

        try:
            serializer.is_valid(raise_exception=True)
        except (AuthenticationFailed, ValidationError) as exc:
            return Response(exc.detail, exc.status_code)

        return Response(
            {
                'success': _('Your password has been reset successfully.'),
                'credentials': serializer.save()
            }, status.HTTP_202_ACCEPTED)
