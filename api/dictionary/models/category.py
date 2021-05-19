from enum import Enum
from django.utils.translation import gettext_lazy as _
from api.models import TimestampedModel


class Category(Enum):
    """
    Enumerated type for icon/word categories.
    """
    ADJECTIVE = 0
    ADVERB = 1
    CONNECTIVE = 2
    NOUN = 3
    PREPOSITION = 4
    PUNCTUATION = 5
    VERB_IRREGULAR = 6
    VERB_MODAL = 7
    VERB_REGULAR = 8
    VERB_TWO_PART = 9


CATEGORY_CHOICES = [
    (Category.ADJECTIVE, _('Adjective')),
    (Category.ADVERB, _('Adverb')),
    (Category.CONNECTIVE, _('Connective')),
    (Category.NOUN, _('Noun')),
    (Category.PREPOSITION, _('Preposition')),
    (Category.PUNCTUATION, _('Punctuation')),
    (Category.VERB_IRREGULAR, _('Irregular Verb')),
    (Category.VERB_MODAL, _('Modal Verb')),
    (Category.VERB_REGULAR, _('Regular Verb')),
    (Category.VERB_TWO_PART, _('Two-Part Verb')),
]