from django.conf import settings
from django.core.paginator import (Paginator, InvalidPage, PageNotAnInteger)
from django.shortcuts import get_object_or_404
from django.http import Http404

from rest_framework import status, serializers, generics
from rest_framework.exceptions import (
    ErrorDetail, NotAuthenticated, PermissionDenied, NotFound, ValidationError)
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
        Action to upload an icon and associate it with a corresponding dictionary entry.
        """
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

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


class IconsRetrieveView(generics.GenericAPIView):
    """
    An API View for retrieving data for multiple icons.
    """
    serializer_class = IconRetrieveSerializer

    def __success_response(self, paginator, page):
        return Response(
            {
                'results': [x.obj for x in page.object_list],
                'pagination': {
                    'totalResults': paginator.count,
                    'maxResultsPerPage': paginator.per_page,
                    'numResultsThisPage': len(page.object_list),
                    'thisPageNumber': page.number,
                    'totalPages': paginator.num_pages,
                    'prevPageExists': page.has_previous(),
                    'nextPageExists': page.has_next(),
                }
            },
            status=status.HTTP_200_OK,
        )

    def get(self, request):
        """
        Action to retrieve data pertaining to an icon, including ID, image data, and a MD5 hashsum.
        """
        part_speech = request.GET.get('partSpeech', 'any')
        page_num = request.query_params.get('page', 1)
        results_per_page = min(
            request.query_params.get(
                'results', settings.DEFAULT_RESULTS_PER_PAGE),
            settings.MAX_RESULTS_PER_PAGE,
        )

        if part_speech == 'any':
            icons = Icon.objects.all().order_by('word')
        elif part_speech in Icon.PART_SPEECH.__set__:
            icons = Icon.objects.filter(
                part_speech=Icon.PART_SPEECH.STR_TO_ID[part_speech]).order_by('word')
        else:
            return Response(
                {
                    NON_FIELD_ERRORS_KEY: [
                        ErrorDetail(
                            'The request was invalid. Make sure "partSpeech" is one of the following: "adjective", "adverb", "connective", "noun", "preposition", "punctuation", "verb_2_part", "verb_irregular", "verb_modal", or "verb_regular".',
                            'bad_request')
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST)

        paginator = Paginator(icons, results_per_page)
        try:
            page = paginator.get_page(page_num)
        except PageNotAnInteger:
            return self.__error_response(
                ErrorDetail(
                    _('Query parameter "page" must be an integer.'),
                    'invalid_type'),
                status.HTTP_400_BAD_REQUEST,
            )
        except InvalidPage:
            return self.__error_response(
                ErrorDetail(
                    _('Query parameter "page" does not exist.'),
                    'invalid_page_num'),
                status.HTTP_404_NOT_FOUND,
            )

        return self.__success_response(paginator, page)
