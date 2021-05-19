import inspect

from django.db import models
from django.utils.translation import gettext_lazy as _

from .dict_entry import DictionaryEntry

NOT_IMPLEMENTED_ERROR = NotImplementedError(
    _(
        'Object is an instance of Word, which must be implemented by Homograph or SingleEntry.'
    ))


class Word:
    """
    Informal interface to be realized by Homograph or SingleEntry.
    """
    @property
    def entries(self):
        raise NOT_IMPLEMENTED_ERROR

    @property
    def is_homograph(self):
        raise NOT_IMPLEMENTED_ERROR

    @property
    def words(self):
        raise NOT_IMPLEMENTED_ERROR


class Homograph(Word):
    """
    A Word containing multiple entries.
    """
    class EntriesNotDefined(Exception):
        """
        Exception to be raised when self.__entries is not defined.
        """
        def __init__(self):
            """
            Initialization method called at exception creation. Here, the error message is defined.
            """
            super().__init__(
                _('self.__entries must be defined to use this method.'))

    __entries = None

    def __init__(self, entries):
        """
        Initialization method called at object creation. Here, self.__entries is populated after verifying that the parameter 'entries' contains a list of multiple DictionaryEntry objects.
        """
        assert isinstance(entries, list), \
            "Parameter 'entries' must be a list of DictionaryEntry instances."
        assert len(entries) > 1, \
            'Homograph instances must contain more than one DictionaryEntry.'
        for entry in entries:
            assert isinstance(entry, DictionaryEntry), \
                "Parameter 'entries' must only contain DictionaryEntry instances."

        self.__entries = entries

    @property
    def entries(self):
        return self.__entries

    @property
    def is_homograph(self):
        return True

    @property
    def word(self):
        return self.__entries[0].id.split(':')[0]


class SingleEntry(Word):
    """
    A Word containing a single entry.
    """
    __entry = None

    def __init__(self, entry):
        """
        Initialization method called at object creation. Here, self.__entry is populated after verifying that the parameter 'entry' contains a DictionaryEntry object.
        """
        assert isinstance(entry, DictionaryEntry), \
            "Parameter 'entry' must be a DictionaryEntry instance."
        self.__entry = entry

    @property
    def entries(self):
        return [self.__entry]

    @property
    def is_homograph(self):
        return False

    @property
    def word(self):
        return self.__entry.id
