from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response

from api import NON_FIELD_ERRORS_KEY

from ..models import Icon


class IconViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for uploading or approving icons.
    """
    def __bad_request(self):
        return Response(
            {
                NON_FIELD_ERRORS_KEY: [
                    ErrorDetail(
                        'The request was invalid. Be sure to include an image of maximum width 60 pixels and exact height 54 pixels.',
                        'bad_request')
                ]
            },
            status=status.HTTP_400_BAD_REQUEST)

    def upload(self, request):
        icon = request.FILES.get('icon')
        if not icon:
            return self.__bad_request()

        try:
            icon = Icon.objects.create(image=icon)
        except Icon.InvalidImageError as exc:
            return self.__bad_request()

        return Response(
            {'success': 'File upload successful.'}, status=status.HTTP_200_OK)

    def approve(self, request, id):
        queryset = Icon.objects.all()
        icon = get_object_or_404(queryset, id=id)
        icon.is_approved = True
        icon.save()

        return Response(
            {'success': 'Icon approved.'}, status=status.HTTP_200_OK)