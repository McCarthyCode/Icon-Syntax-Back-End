import json
import requests
import string

from django.conf import settings


class ExternalAPIManager:
    """
    Class defining utility methods for sending requests to an external API.
    """
    __num_api_calls = 0

    @classmethod
    def num_api_calls(cls):
        """
        Class method returning the number of calls to the external API since the value was last set or reset.
        """
        if settings.COUNT_API_CALLS:
            return cls.__num_api_calls
        else:
            raise AttributeError(
                f"type object '{cls.__name__}' has no attribute 'num_api_calls'"
            )

    @classmethod
    def reset_num_api_calls(cls):
        """
        Class method resetting the number of calls to the external API.
        """
        if settings.COUNT_API_CALLS:
            cls.__num_api_calls = 0
        else:
            raise AttributeError(
                f"type object '{cls.__name__}' has no attribute 'reset_num_api_calls'"
            )

    @classmethod
    def increment_num_api_calls(cls):
        """
        Class method incrementing the number of calls to the external API.
        """
        if settings.COUNT_API_CALLS:
            cls.__num_api_calls += 1
        else:
            raise AttributeError(
                f"type object '{cls.__name__}' has no attribute 'increment_num_api_calls'"
            )
