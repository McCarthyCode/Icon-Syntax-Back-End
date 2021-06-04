import json
from collections import OrderedDict

from django.conf import settings
from django.core.paginator import (
    Paginator, InvalidPage, EmptyPage, PageNotAnInteger)

from requests.exceptions import RequestException

from rest_framework import generics, status
from rest_framework.response import Response

from api import NON_FIELD_ERRORS_KEY

from ..utils import Util


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
                'results', settings.DEFAULT_RESULTS_PER_PAGE),
            settings.MAX_RESULTS_PER_PAGE,
        )

        response = Util.get_mw_dict(word)
        # The following variable names a list, and is not the dict type.
        # Here, dict refers to a literal dictionary.
        mw_dict = json.loads(response.text)

        # Create results array for use in generating response
        results = mw_dict
        if type(mw_dict) == list:
            # Obtain the appropriate page from the mw_dict list
            if type(mw_dict[0]) == dict:
                meta_fields = {'id', 'sort', 'stems', 'offensive'}
                results = sorted(
                    [
                        {key: x['meta'][key] for key in meta_fields} \
                        for x in mw_dict
                    ],
                    key=lambda y: y['sort'])

            paginator = Paginator(results, results_per_page)
            try:
                page = paginator.get_page(page_num)
            except PageNotAnInteger:
                return self.__error_response(
                    'Query parameter "page" must be an integer.',
                    status.HTTP_400_BAD_REQUEST,
                )
            except InvalidPage:
                return self.__error_response(
                    'Query parameter "page" is invalid.',
                    status.HTTP_404_NOT_FOUND,
                )

            # if type(mw_dict[0]) == str:
            #     return self.__generate_response(paginator, page)

            return self.__success_response(paginator, page)
        elif type(mw_dict) == str:
            if mw_dict == 'Word is required.':
                return self.__error_response(
                    mw_dict, status.HTTP_400_BAD_REQUEST)

        return self.__error_response(
            'Unhandled API error. Please contact the site administrator at webmaster@iconopedia.org.',
            status.HTTP_500_INTERNAL_SERVER_ERROR)
