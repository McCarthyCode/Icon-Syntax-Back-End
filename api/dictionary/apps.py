from django.apps import AppConfig


class DictionaryConfig(AppConfig):
    """
    Class defining app configurations.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.dictionary'
