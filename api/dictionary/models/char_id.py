from django.db import models


class CharID(models.Model):
    """
    Abstract model overriding the default BigAutoField ID with a CharField.
    """
    class Meta:
        """
        The metaclass defining its parent as abstract.
        """
        abstract = True

    id = models.CharField(primary_key=True, max_length=64)
