import json
from collections import OrderedDict

from django.conf import settings
from django.core.paginator import (
    Paginator, InvalidPage, EmptyPage, PageNotAnInteger)

from requests.exceptions import RequestException

from rest_framework import generics, status
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response

from api import NON_FIELD_ERRORS_KEY

from ..models import Word, DictionaryEntry
from ..utils import ExternalAPIManager


class WordSearchView(generics.GenericAPIView):
    """
    View class for getting search results.
    """

    def __error_response(self, message, status):
        return Response({
            NON_FIELD_ERRORS_KEY: [message],
        }, status=status)

    def __success_response(self, paginator, page):
        return Response(
            {
                'results': page.object_list,
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
        GET method for obtaining search results, and creating a new model instance if a results object does not exist or has gone stale.
        """
        page_num = request.query_params.get('page', 1)
        results_per_page = min(
            request.query_params.get(
                'results', settings.DEFAULT_PAGE_LEN['icon']),
            settings.MAX_PAGE_LEN['icon'],
        )

        _word, entries = Word.objects.get_word_and_entries(word)
        if type(entries) == list:
            paginator = Paginator(entries, results_per_page)
        else:
            # The following variable names a list, and is not the dict type.
            # Here, dict refers to a literal dictionary.

            # Create results array for use in generating response
            dict_entries = entries
            meta_fields = {'id', 'sort', 'stems', 'offensive'}
            results = sorted(
                    [
                        {key: json.loads(x.json)['meta'][key] \
                            for key in meta_fields
                        } for x in dict_entries
                    ],
                    key=lambda y: y['sort'])

            paginator = Paginator(results, results_per_page)
        try:
            page = paginator.get_page(page_num)
        except PageNotAnInteger:
            return self.__error_response(
                ErrorDetail(
                    'Query parameter "page" must be an integer.',
                    'invalid_type'),
                status.HTTP_400_BAD_REQUEST,
            )
        except InvalidPage:
            return self.__error_response(
                ErrorDetail(
                    'Query parameter "page" is invalid.', 'invalid_page_num'),
                status.HTTP_404_NOT_FOUND,
            )

        return self.__success_response(paginator, page)
