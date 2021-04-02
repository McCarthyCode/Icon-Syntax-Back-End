import jwt

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.urls import reverse

from rest_framework import status, exceptions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import *
from .utils import Util

from .models import User
from api.authentication.exceptions import ConflictError


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
        except ConflictError as e:
            return Response(e.detail, status.HTTP_409_CONFLICT)
        serializer.save()

        user = User.objects.get(
            username=serializer.validated_data.get('username'))
        token = RefreshToken.for_user(user).access_token

        if settings.STAGE == 'development':
            scheme = 'http'
            domain = 'localhost:8000'
        else:
            scheme = 'https'
            domain = get_current_site(request).domain
        path = reverse('api:auth:verify')
        query_string = f'?token={token}'

        Util.send_email(
            'Verify your email address with Iconopedia',
            'Thank you for registering an account with Iconopedia! Please follow the link below to complete the registration process. If clicking it does not work, try copying the entire URL and pasting it into your address bar.\n\n'
            f'{scheme}://{domain}{path}{query_string}',
            [user.email],
        )

        return Response(
            {
                **serializer.data,
                'success':
                'Step 1 of user registration successful. Check your email for a confirmation link to complete the process.',
            }, status.HTTP_201_CREATED)


class RegisterVerifyView(APIView):
    """
    View for accepting a generated token from a new user to complete the registration process.
    """
    serializer_class = VerifySerializer

    def get(self, request):
        """
        GET method for taking a token from a query string, checking if it is valid, and marking its associated user's email as verified.
        """
        token = request.GET.get('token', None)

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return Response(
                {'error': 'The activation link has expired.'},
                status=status.HTTP_400_BAD_REQUEST)
        except jwt.DecodeError:
            return Response(
                {'error': 'The activation link was invalid.'},
                status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            return Response(
                {
                    'error':
                    'The user associated with this token no longer exists.'
                },
                status=status.HTTP_404_NOT_FOUND)

        if not user.is_verified:
            user.is_verified = True
            user.save()

        serializer = self.serializer_class(data={'username': user.username})
        serializer.is_valid(raise_exception=True)

        return Response(
            {
                'success':
                'You have successfully verified your email address and completed the registration process! You may now access the site\'s full features.',
                **serializer.data,
            },
            status=status.HTTP_200_OK)


class LoginView(GenericAPIView):
    """
    View for taking in an existing user's credentials and authorizing them if valid or denying access if invalid.
    """
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except exceptions.ValidationError as e:
            return Response(
                {
                    'error': 'The credentials used to login were invalid.',
                    **e.detail,
                },
                status=status.HTTP_400_BAD_REQUEST)
        except exceptions.AuthenticationFailed as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.data, status=status.HTTP_200_OK)
