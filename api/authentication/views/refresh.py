from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.authentication import NON_FIELD_ERRORS_KEY
from api.authentication.models import User

from ..serializers import RefreshSerializer


class RefreshView(GenericAPIView):
    """
    View to take a refresh token when an access token is expired and obtain new credentials.
    """
    serializer_class = RefreshSerializer

    def post(self, request):
        """
        POST method for refreshing an access token
        """
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed as exc:
            return Response(
                {NON_FIELD_ERRORS_KEY: [exc.detail]}, exc.status_code)

        return Response(
            {
                'success': str(_('You have successfully refreshed.')),
                'credentials': serializer.validated_data['user'].credentials
            },
            status=status.HTTP_200_OK)
