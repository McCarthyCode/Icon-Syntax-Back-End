from django.conf import settings
from django.core.paginator import (Paginator, InvalidPage, PageNotAnInteger)

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from api.authentication.permissions import IsSafeMethod, IsVerified, IsOwner

from ..models import Post
from ..serializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Post.Comment.objects.all()
    permission_classes = [IsSafeMethod | IsAdminUser | (IsVerified & IsOwner)]

    def get_queryset(self, *args, **kwargs):
        return Post.Comment.objects.filter(*args, **kwargs)

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={
                'user': request.user,
                'method': request.method
            })
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
            context={'method': request.method})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
