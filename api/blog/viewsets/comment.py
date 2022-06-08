from django.conf import settings
from django.core.paginator import (Paginator, InvalidPage, PageNotAnInteger)

from rest_framework import viewsets, status
from rest_framework.response import Response

from ..models import Post
from ..serializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Post.Comment.objects.all()

    def get_queryset(self, *args, **kwargs):
        self.queryset = Post.Comment.objects.filter(*args, **kwargs)
        return self.queryset

    def list(self, request):
        page_num = request.query_params.get('page', 1)
        post = request.query_params.get('post', None)
        results_per_page = min(
            request.query_params.get(
                'results', settings.DEFAULT_PAGE_LEN['comment']),
            settings.MAX_PAGE_LEN['comment'],
        )

        comments = self.get_queryset(
            post__pk=post, parent=None).order_by('-updated')
        paginator = Paginator(comments, results_per_page)

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
                f'Listing {len(page.object_list)} of {paginator.count} comment{"" if paginator.count == 1 else "s"}.',
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
