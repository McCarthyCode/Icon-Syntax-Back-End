from django.conf import settings
from django.core.paginator import (Paginator, InvalidPage, PageNotAnInteger)
from django.utils.translation import gettext_lazy as _

from rest_framework import generics, status
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response

from api import NON_FIELD_ERRORS_KEY
from ..models import Icon


class IconSearchView(generics.GenericAPIView):
    """
    View class for getting search results.
    """

    def __error_response(self, error_detail, status):
        return Response(
            {
                NON_FIELD_ERRORS_KEY: [error_detail],
            }, status=status)

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

    def get(self, request, word):
        """
        GET method for obtaining search results.
        """
        page_num = request.query_params.get('page', 1)
        results_per_page = min(
            request.query_params.get(
                'results', settings.DEFAULT_PAGE_LEN['icon']),
            settings.MAX_PAGE_LEN['icon'],
        )

        entries = Icon.objects.filter(word__icontains=word).extra(
            select={'relevance': 'char_length(word)'}, order_by=['relevance'])
        paginator = Paginator(entries, results_per_page)

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
