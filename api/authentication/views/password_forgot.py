from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed, NotAuthenticated, PermissionDenied, ValidationError)
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.authentication import NON_FIELD_ERRORS_KEY
from api.authentication.permissions import IsSafeMethod

from ..permissions import IsVerified
from ..serializers import (
    PasswordForgotSerializer, PasswordResetSerializer,
    PasswordForgotVerifySerializer)
from ..utils import Util


class PasswordForgotView(GenericAPIView):
    """
    Endpoint for first step of resetting a forgotten password.
    """
    serializer_class = PasswordForgotSerializer

    def post(self, request):
        """
        POST method for first step of forgot password process.
        """
        verify = request.query_params.get(
            'verify', settings.FRONT_END_VERIFY_PATHS['PASSWORD_FORGOT'])
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exc:
            return Response(exc.detail, exc.status_code)
        user = serializer.save()

        if not user.is_anonymous:
            Util.send_email_link(
                _('Reset your forgotten password with Icon Syntax'),
                _(
                    'We have received a request to reset a forgotten password. Please follow the link below to complete the password reset process. If clicking it does not work, try copying the entire URL and pasting it into your address bar.'
                ),
                user,
                verify,
            )

        return Response(
            {
                'success':
                str(
                    _(
                        'If the email provided is valid, a password reset link should appear in your inbox within a few minutes. Please be sure to check your spam folder.'
                    ))
            }, status.HTTP_200_OK)


class PasswordForgotVerifyView(GenericAPIView):
    """
    Endpoint for last step of resetting a forgotten password.
    """
    serializer_class = PasswordForgotVerifySerializer
    permission_classes = [IsSafeMethod | (IsAuthenticated & IsVerified)]

    def post(self, request):
        """
        POST method for last step of forgot password process.
        """
        serializer = self.serializer_class(
            data=request.data, context={'user': request.user})

        try:
            serializer.is_valid(raise_exception=True)
        except (AuthenticationFailed, ValidationError) as exc:
            return Response(exc.detail, exc.status_code)

        user = serializer.save()

        return Response(
            {
                'success': _('Your password has been reset successfully.'),
                'credentials': user.credentials
            }, status.HTTP_202_ACCEPTED)
