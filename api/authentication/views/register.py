from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed, ErrorDetail, NotAuthenticated, ValidationError)
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken

from ..exceptions import ConflictError
from ..models import User
from ..serializers.register import *
from ..utils import Util


class RegisterView(GenericAPIView):
    """
    View for taking in a new user's credentials and sending a confirmation email to verify.
    """
    serializer_class = RegisterSerializer

    def post(self, request):
        """
        POST method that performs validation, creates a user instance, and sends a verification email.
        """
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exc:
            for key, errors in exc.detail.items():
                for error in errors:
                    if error.code == f'{key}_exists':
                        return Response(exc.detail, status.HTTP_409_CONFLICT)
            return Response(exc.detail, exc.status_code)

        Util.send_email_link(
            _('Verify your email address with Iconopedia'),
            _(
                'Thank you for registering an account with Iconopedia! Please follow the link below to complete the registration process. If clicking it does not work, try copying the entire URL and pasting it into your address bar.'
            ),
            serializer.save(),
            reverse('api:auth:verify'),
        )

        return Response(
            {
                'success':
                _(
                    'Step 1 of user registration successful. Check your email for a confirmation link to complete the process.'
                ),
                **serializer.data
            }, status.HTTP_201_CREATED)


class RegisterVerifyView(APIView):
    """
    View for accepting a generated token from a new user to complete the registration process.
    """
    serializer_class = RegisterVerifySerializer

    def initial(self, request, *args, **kwargs):
        """
        This method overrides the default APIView method so exceptions can be handled.
        """
        try:
            super().initial(request, *args, **kwargs)
        except InvalidToken as exc:
            detail = exc.detail['detail'] \
                if 'detail' in exc.detail else exc.detail

            # Append a period because punctuation errors are annoying.
            if detail[-1] not in '.?!':
                detail = ErrorDetail(str(detail) + '.', detail.code)

            raise AuthenticationFailed(
                {NON_FIELD_ERRORS_KEY: [detail]}, detail.code)

    def post(self, request):
        """
        POST method for taking a token from a query string, checking if it is valid, and marking its associated user's email address as verified.
        """
        serializer = self.serializer_class(
            data={}, context={'user': request.user})

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exc:
            return Response(exc.detail, exc.status_code)

        serializer.save()

        return Response(
            {
                'success':
                _(
                    'You have successfully verified your email address and completed the registration process! You may now access the site\'s full features.'
                ),
                **serializer.validated_data
            },
            status=status.HTTP_200_OK)
