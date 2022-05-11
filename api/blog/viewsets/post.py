from collections import OrderedDict

from django.conf import settings
from django.core.paginator import (Paginator, InvalidPage, PageNotAnInteger)

from rest_framework import viewsets, status
from rest_framework.response import Response

from api import NON_FIELD_ERRORS_KEY

from ..models import Post
from ..serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def __error_response(self, error_detail, status):
        return Response(
            {
                NON_FIELD_ERRORS_KEY: [error_detail],
            }, status=status)

    def get_queryset(self, *args, **kwargs):
        self.queryset = Post.objects.filter(*args, **kwargs)
        return self.queryset

    def list(self, request):
        page_num = request.query_params.get('page', 1)
        results_per_page = min(
            request.query_params.get(
                'results', settings.DEFAULT_RESULTS_PER_PAGE),
            settings.MAX_RESULTS_PER_PAGE,
        )

        posts = sorted(self.get_queryset(), key=lambda x: x.created)
        paginator = Paginator(posts, results_per_page)

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
                f'Found {paginator.count} post{"" if paginator.count == 1 else "s"}.',
                'data': [
                    OrderedDict(
                        {
                            'title': x.title,
                            'content': x.content[:500],
                            'created': x.created,
                            'updated': x.updated
                        }) for x in page.object_list
                ],
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