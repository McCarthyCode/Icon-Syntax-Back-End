from django.conf import settings
from django.core.paginator import (Paginator, InvalidPage, PageNotAnInteger)
from django.db.models.signals import post_save
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions, status
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api import NON_FIELD_ERRORS_KEY
from api.exceptions import BadRequestError

from ..models import Icon
from ..serializers.icon_serializers import *


class IconsViewSet(GenericViewSet):
    queryset = Icon.objects.all()

    def __error_response(self, error_detail, status):
        return Response(
            {
                NON_FIELD_ERRORS_KEY: [error_detail],
            }, status=status)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = []
        else:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]

    def list(self, request):
        if request.method != 'GET':
            raise exceptions.MethodNotAllowed(request.method)

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
                category.id, filter_kwargs={'word__istartswith': search})
        elif search and not category_id:
            icons = list(Icon.objects.filter(word__istartswith=search))
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

        return Response(
            {
                'success':
                f'Found {paginator.count} icon{"" if paginator.count == 1 else "s"}.',
                'data': [x.obj for x in page.object_list],
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

    def retrieve(self, request, *args, **kwargs):
        if request.method != 'GET':
            raise exceptions.MethodNotAllowed(request.method)

        return Response(
            {
                'success': 'Found an icon with the specified ID.',
                'data': get_object_or_404(Category, *args, **kwargs).obj
            },
            status=status.HTTP_200_OK,
        )

    def create(self, request):
        if request.method != 'POST':
            raise exceptions.MethodNotAllowed(request.method)

        print(request.data)

        serializer = IconUploadSerializer(
            data=request.data, context={'request': request})

        if not serializer.is_valid():
            raise BadRequestError(detail=serializer.errors)

        category = serializer.save()

        return Response(
            {
                'success': 'You have successfully uploaded an icon.',
                'data': category.obj
            },
            status=status.HTTP_201_CREATED)

    def update(self, request, id):
        if request.method not in ['PATCH', 'PUT']:
            raise exceptions.MethodNotAllowed(request.method)

        icon = get_object_or_404(Icon, id=id)

        serializer = IconUpdateSerializer(
            data=request.data, instance=icon, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)

        icon = serializer.save()

        return Response(
            {
                'success': 'You have successfully updated an icon',
                'data': icon.obj
            },
            status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        if request.method != 'DELETE':
            raise exceptions.MethodNotAllowed(request.method)

        icon = get_object_or_404(Icon, pk=pk)

        post_save.disconnect(Image.post_save, sender=Icon, dispatch_uid='0')
        icon.delete()
        post_save.connect(Image.post_save, sender=Icon, dispatch_uid='0')

        return Response(status=status.HTTP_204_NO_CONTENT)
