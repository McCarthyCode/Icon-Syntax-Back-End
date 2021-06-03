import json
from collections import OrderedDict

from django.conf import settings
from django.core.paginator import Paginator

from requests.exceptions import RequestException

from rest_framework import generics, status
from rest_framework.response import Response

from api import NON_FIELD_ERRORS_KEY

from ..models import CachedSearchTerm
from ..utils import Util


class WordSearchView(generics.GenericAPIView):
    """
    View class for getting search results.
    """
    def get(self, request, word):
        """
        GET method for obtaining search results, and creating a new model instance if a results object does not exist or has gone stale.
        """
        breakpoint()
        page = request.query_params.get('page', 1)
        results_per_page = min(
            request.query_params.get(
                'results', settings.DEFAULT_RESULTS_PER_PAGE),
            settings.MAX_RESULTS_PER_PAGE,
        )

        response = Util.get_mw_dict(word)
        # The following variable names a list, and is not the dict type.
        # Here, dict refers to a literal dictionary.
        mw_dict = json.loads(response.text)

        if type(mw_dict) == list:
            if type(mw_dict[0]) == str:
                paginator = Paginator(mw_dict, results_per_page)

                return Response(
                    {
                        'results': paginator.page(page),
                        'resultsPerPage': results_per_page,
                        'page': page,
                        'pages': paginator.num_pages
                    },
                    status=status.HTTP_200_OK,
                )

            meta_fields = {'id', 'sort', 'stems', 'offensive'}
            results = sorted(
                [
                    {key: x['meta'][key] for key in meta_fields} \
                    for x in mw_dict
                ],
                key=lambda y: y['sort'])
        else:
            return Response(
                {
                    'results': [],
                    'resultsPerPage': results_per_page,
                    'page': 0,
                    'pages': 0
                },
                status=status.HTTP_200_OK)
        '''
        cached_search_term = None
        try:
            cached_search_term = CachedSearchTerm.objects.get(mw=word)
        except CachedSearchTerm.DoesNotExist:
            try:
                response = Util.get_mw_dict(word)
            except RequestException:
                return Response(
                    {
                        NON_FIELD_ERRORS_KEY: [
                            ErrorDetail(
                                'There was an issue retriveing the word entry. If the problem persists, please contact support at support@iconopedia.org.',
                                'request_error')
                        ]
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            kwargs = {
                'term': word,
                'mw': word,
                'data': response.text,
            }

            breakpoint()
            cached_search_term = CachedSearchTerm.objects.create(**kwargs)

            mw_content = json.loads(cached_search_term.data)
            if type(mw_content) == list:
                if type(mw_content[0]) == str:
                    return Response(
                        {
                            'results': paginator.page(page),
                            'resultsPerPage': results_per_page,
                            'page': page,
                            'pages': paginator.num_pages
                        },
                        status=status.HTTP_200_OK,
                    )

                meta_fields = {'id', 'sort', 'stems', 'offensive'}
                results = sorted(
                    [
                        {k: x['meta'][k] for k in meta_fields} \
                            for x in mw_content
                    ],
                    key=lambda y: y['sort'])

                        # results = set(
                        #     [
                        #         tuple(entry['meta'][x] for x in meta_fields)
                        #         for entry in mw_content
                        #     ])

                        # breakpoint()
                        # results = [
                        #     {
                        #         'id': entry['meta']['id'],
                        #         'stems': entry['meta']['stems'],
                        #         'offensive': entry['meta']['offensive'],
                        #     } for entry in mw_content
                        # ]
                        # suggestions = {}
                        # for id_str, sort in results:
                        #     suggestions = {
                        #         **suggestions,
                        #         id_str.split(':')[0]: {
                        #             'sort': sort
                        #         }
                        #     }

                        # breakpoint()
                        # suggestions = OrderedDict(
                        #     sorted(
                        #         OrderedDict(suggestions),
                        #         key=lambda x: int(x['sort']),
                        #     ))

                        # pp.pprint([entry['meta'] for entry in mw_content])
                        # pp.pprint(suggestions)
                        # pp.pprint(
                        #     [
                        #         {
                        #             'id': mw_content[0]['meta'][key],
                        #         } for key in mw_content[0]['meta']
                        #     ])
                    else:
                        return Response(
                            {
                                'results': [],
                                'resultsPerPage': results_per_page,
                                'page': 0,
                                'pages': 0
                            },
                            status=status.HTTP_200_OK)
        '''
        paginator = Paginator(suggestions, results_per_page)

        return Response(
            {
                'results': paginator.page(page),
                'resultsPerPage': results_per_page,
                'page': page,
                'pages': paginator.num_pages
            },
            status=status.HTTP_200_OK,
        )
