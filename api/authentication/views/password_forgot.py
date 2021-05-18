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

from ..permissions import IsVerified
from ..serializers import PasswordForgotSerializer, PasswordResetSerializer
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
                _('Reset your forgotten password with Iconopedia'),
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
        POST method for last step of forgot password process.
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
