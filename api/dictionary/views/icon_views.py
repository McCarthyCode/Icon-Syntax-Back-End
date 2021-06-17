from django.shortcuts import get_object_or_404
from django.http import Http404

from rest_framework import status, serializers, generics
from rest_framework.exceptions import (
    ErrorDetail, NotAuthenticated, PermissionDenied, NotFound)
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from api import NON_FIELD_ERRORS_KEY
from api.authentication.permissions import IsVerified

from ..models import Icon
from ..serializers import (
    IconUploadSerializer, IconApproveSerializer, IconRetrieveSerializer)


class IconUploadView(generics.GenericAPIView):
    """
    An API View for uploading an icon.
    """
    serializer_class = IconUploadSerializer
    permission_classes = [IsAuthenticated, IsVerified]

    def __bad_request(self):
        """
        Returns a token HTTP 400 response.
        """
        return Response(
            {
                NON_FIELD_ERRORS_KEY: [
                    ErrorDetail(
                        'The request was invalid. Be sure to include an image of maximum width 60 pixels and exact height 54 pixels.',
                        'bad_request')
                ]
            },
            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """
        Action to upload an icon.
        """
        icon = request.FILES.get('icon')
        if not icon:
            return self.__bad_request()

        try:
            icon = Icon.objects.create(image=icon)
        except Icon.InvalidImageError as exc:
            return self.__bad_request()

        if request.user.is_superuser:
            icon.is_approved = True
            icon.save()

        return Response(
            {'success': 'File upload successful.'}, status=status.HTTP_200_OK)


class IconApproveView(generics.GenericAPIView):
    """
    An API View for approving a user-submitted icon.
    """
    serializer_class = IconApproveSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, id):
        """
        Action to approve an icon.
        """
        queryset = Icon.objects.all()
        icon = get_object_or_404(queryset, id=id)
        icon.is_approved = True
        icon.save()

        return Response(
            {'success': 'Icon approved.'}, status=status.HTTP_200_OK)


class IconRetrieveView(generics.GenericAPIView):
    """
    An API View for retrieving icon data.
    """
    serializer_class = IconRetrieveSerializer

    def get(self, request, id):
        """
        Action to retrieve data pertaining to an icon, including ID, image data, and a MD5 hashsum.
        """
        icon = get_object_or_404(Icon, id=id)

        return Response(icon.obj, status=status.HTTP_200_OK)
