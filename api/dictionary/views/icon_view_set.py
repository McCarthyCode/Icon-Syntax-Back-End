from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.exceptions import ErrorDetail, NotAuthenticated, PermissionDenied
from rest_framework.response import Response

from api import NON_FIELD_ERRORS_KEY
from api.authentication.permissions import IsVerified

from ..models import Icon


class IconViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for uploading or approving icons.
    """
    def initial(self, request, *args, **kwargs):
        """
        This method overrides the default ViewSet method so exceptions can be handled.
        """
        try:
            super().initial(request, *args, **kwargs)
        except NotAuthenticated as exc:
            detail = exc.detail['detail'] \
                if 'detail' in exc.detail else exc.detail

            # Append a period because punctuation errors are annoying.
            if detail[-1] not in '.?!':
                detail = ErrorDetail(str(detail) + '.', detail.code)

            raise NotAuthenticated(
                {NON_FIELD_ERRORS_KEY: [detail]}, detail.code)
        except PermissionDenied as exc:
            detail = exc.detail['detail'] \
                if 'detail' in exc.detail else exc.detail

            # Append a period because punctuation errors are annoying.
            if detail[-1] not in '.?!':
                detail = ErrorDetail(str(detail) + '.', detail.code)

            raise PermissionDenied(
                {NON_FIELD_ERRORS_KEY: [detail]}, detail.code)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method.lower() == 'options':
            return [AllowAny()]

        permission_classes = {
            'upload': [IsAuthenticated, IsVerified],
            'approve': [IsAdminUser],
        }

        return [permission() for permission in permission_classes[self.action]]

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

    def upload(self, request):
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

        return Response(
            {'success': 'File upload successful.'}, status=status.HTTP_200_OK)

    def approve(self, request, id):
        """
        Action to approve an icon.
        """
        queryset = Icon.objects.all()
        icon = get_object_or_404(queryset, id=id)
        icon.is_approved = True
        icon.save()

        return Response(
            {'success': 'Icon approved.'}, status=status.HTTP_200_OK)
