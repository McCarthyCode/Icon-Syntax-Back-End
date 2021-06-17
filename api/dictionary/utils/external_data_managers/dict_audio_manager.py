import requests
from api.dictionary.models import MP3
from .external_api_manager import ExternalAPIManager


class DictionaryAudioManager(ExternalAPIManager):
    """
    Class defining utility methods for downloading audio files from the Merriam-Webster media servers.
    """
    @staticmethod
    def __get_mp3(id):
        """
        Private method for obtaining a MP3 file from the Merriam-Webster media servers.
        """
        subdir = id[0]
        for substr in {'bix', 'gg'}:
            if id[:len(substr)] == substr:
                subdir = substr

        if subdir in string.punctuation + string.digits:
            subdir = 'number'

        return requests.get(
            f'https://media.merriam-webster.com/audio/prons/en/us/mp3/{subdir}/{id}.mp3'
        )

    @staticmethod
    def get_mp3(id):
        """
        Public wrapper for private method __get_mp3(). Obtains a MP3 file from local storage if a cache entry exists, and downloads from the Merriam-Webster database on a cache miss.
        """
        mp3 = None

        try:
            mp3 = MP3.objects.get(id=id)
        except MP3.DoesNotExist:
            mp3 = MP3.objects.create(id=id)

            response = ExternalAPIManager.__get_mp3(word)
            data = json.loads(response.text)

        return _word, DictionaryEntry.objects.filter(word=_word)