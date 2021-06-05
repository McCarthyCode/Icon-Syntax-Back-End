from api.models import TimestampedModel
from .image import Image


class Icon(TimestampedModel, Image):
    """
    Image file associated with zero or more WordEntries.
    """
    pass
