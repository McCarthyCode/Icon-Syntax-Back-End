import jwt

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.urls import reverse

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import RegisterSerializer
from .utils import Util

from api.authentication.models import User


class RegisterView(GenericAPIView):
    """
    View for taking in a new user's credentials and sending a confirmation email to verify.
    """
    serializer_class = RegisterSerializer

    def post(self, request):
        """
        POST method that performs validation, creates a user instance, and sends a verication email.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
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
            'Thank you for registering an account with Iconopedia! Please '
            'follow the link below to complete the registration process. If '
            'the link does not work, try copying and pasting the URL into your '
            'address bar.\n\n'
            f'{scheme}://{domain}{path}{query_string}',
            [user.email],
        )

        return Response(
            {
                **serializer.data,
                'success':
                'Step 1 of user registration successful. Check your email for '
                'a confirmation link to complete the process.',
            }, status.HTTP_201_CREATED)


class VerifyView(APIView):
    """
    View for accepting a generated token from a new user to complete the registration process.
    """
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
                {'error': 'The specified user does not exist.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not user.is_verified:
            user.is_verified = True
            user.save()

        return Response(
            {
                'success':
                'You have successfully verified your email address and '
                'completed the registration process! You may now login.'
            },
            status=status.HTTP_200_OK)
