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


class WordView(generics.GenericAPIView):
    """
    View class for getting a word and associated data.
    """
    def get(self, request, word):
        """
        GET method to obtain a word and its associated data.
        """
        _word, entries = Word.objects.get_word_and_entries(word)

        if not _word or not entries:
            return Response(
                {
                    NON_FIELD_ERRORS_KEY:
                    [ErrorDetail(f"Word '{word}' not found.", 'not_found')],
                },
                status=status.HTTP_404_NOT_FOUND)

        return Response(_word.obj, status=status.HTTP_200_OK)
