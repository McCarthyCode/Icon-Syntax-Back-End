from collections import OrderedDict

from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from .image import Image


class Icon(Image):
    """
    Image file associated with a word, a descriptor, a part of speech, and (for verbs) tense.
    """

    # Choices definitions
    class PART_SPEECH:
        NONE = 0
        ADJECTIVES = 1
        ADVERBS = 2
        CONNECTIVES = 3
        NOUNS = 4
        PREPOSITIONS = 5
        PUNCTUATION = 6
        VERBS_2_PART = 7
        VERBS_IRREGULAR = 8
        VERBS_MODALS = 9
        VERBS_REGULAR = 10

        CHOICES = (
            (NONE, 'no category'),
            (ADJECTIVES, 'adjectives'),
            (ADVERBS, 'adverbs'),
            (CONNECTIVES, 'connectives'),
            (NOUNS, 'nouns'),
            (PREPOSITIONS, 'prepositions'),
            (PUNCTUATION, 'punctuation'),
            (VERBS_2_PART, 'verbs 2-part'),
            (VERBS_IRREGULAR, 'verbs irregular'),
            (VERBS_MODALS, 'verbs modals'),
            (VERBS_REGULAR, 'verbs regular'),
        )

    class TENSE:
        NONE = 0
        PRESENT = 1
        PRESENT_PARTICIPLE = 2
        PAST = 3
        PAST_PARTICIPLE = 4

        CHOICES = (
            (NONE, 'no tense'),
            (PRESENT, 'present'),
            (PRESENT_PARTICIPLE, 'present participle'),
            (PAST, 'past'),
            (PAST_PARTICIPLE, 'past participle'),
        )

    # Static variables
    BLOCK_SIZE = 2**12

    # Attributes
    word = models.CharField(max_length=32)
    descriptor = models.CharField(blank=True, null=True, max_length=64)
    part_speech = models.PositiveSmallIntegerField(
        default=PART_SPEECH.NONE, choices=PART_SPEECH.CHOICES)
    tense = models.PositiveSmallIntegerField(
        default=TENSE.NONE, choices=TENSE.CHOICES)
    is_approved = models.BooleanField(default=False)

    @property
    def obj(self):
        """
        Serialize relevant fields and properties for JSON output.
        """
        part_speech_dict = {
            self.PART_SPEECH.NONE: None,
            self.PART_SPEECH.ADJECTIVES: 'adjectives',
            self.PART_SPEECH.ADVERBS: 'adverbs',
            self.PART_SPEECH.CONNECTIVES: 'connectives',
            self.PART_SPEECH.NOUNS: 'nouns',
            self.PART_SPEECH.PREPOSITIONS: 'prepositions',
            self.PART_SPEECH.PUNCTUATION: 'punctuation',
            self.PART_SPEECH.VERBS_2_PART: 'verbs 2-part',
            self.PART_SPEECH.VERBS_IRREGULAR: 'verbs irregular',
            self.PART_SPEECH.VERBS_MODALS: 'verbs modals',
            self.PART_SPEECH.VERBS_REGULAR: 'verbs regular',
        }
        tense_dict = {
            self.TENSE.NONE: None,
            self.TENSE.PRESENT: 'present',
            self.TENSE.PRESENT_PARTICIPLE: 'present participle',
            self.TENSE.PAST: 'past',
            self.TENSE.PAST_PARTICIPLE: 'past participle',
        }

        return OrderedDict(
            {
                'id': self.id,
                'word': self.word,
                'descriptor': self.descriptor,
                'part_speech': part_speech_dict[self.part_speech],
                'tense': tense_dict[self.tense],
                'icon': self.b64,
                'md5': self.md5,
            })


post_save.connect(Image.post_save, sender=Icon, dispatch_uid='0')
