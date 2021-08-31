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

from ..models import Icon, Category
from ..serializers import (IconUploadSerializer, IconApproveSerializer)


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
                        'The request was invalid. Be sure to include an image of maximum width 64 pixels and exact height 54 pixels.',
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

        icon = serializer.save()

        return Response(
            {
                'success': 'File upload successful.',
                'icon': icon.obj
            },
            status=status.HTTP_201_CREATED)


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

    # serializer_class = IconRetrieveSerializer

    def get(self, request, id):
        """
        Action to retrieve data pertaining to an icon, including ID, image data, and a MD5 hashsum.
        """
        icon = get_object_or_404(Icon, id=id)

        return Response(icon.obj, status=status.HTTP_200_OK)


class IconListView(generics.GenericAPIView):
    """
    An API View for listing multiple icons.
    """

    # serializer_class = IconListSerializer

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
        search = request.query_params.get('search', None)
        category_id = request.query_params.get('category', None)
        page_num = request.query_params.get('page', 1)

        results_per_page = min(
            request.query_params.get(
                'results', settings.DEFAULT_RESULTS_PER_PAGE),
            settings.MAX_RESULTS_PER_PAGE,
        )

        icons = []
        if search and category_id:
            category = get_object_or_404(Category, id=category_id)
            icons = Icon.by_category(
                category.id, filter_kwargs={'word__icontains': search})
        elif search and not category_id:
            icons = list(Icon.objects.filter(word__icontains=search))
        elif not search and category_id:
            category = get_object_or_404(Category, id=category_id)
            icons = Icon.by_category(category.id)
        else:
            icons = list(Icon.objects.all())

        icons = sorted(icons, key=lambda x: x.word.lower())
        if search:
            icons = sorted(icons, key=lambda x: len(x.word))

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
