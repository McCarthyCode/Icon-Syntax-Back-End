import os
import re
import string

from functools import partial

from django.core.files.base import ContentFile
from django.core.management.base import CommandError
from django.db.models.signals import post_save

from ..models import Word, Image, Icon


class BulkUploader:
    """
    Class defining a utility method for uploading multiple icons.
    """
    COUNT = 1
    PART_SPEECH_DICT = {
        'adjectives': Icon.PART_SPEECH.ADJECTIVES,
        'adverbs': Icon.PART_SPEECH.ADVERBS,
        'connectives': Icon.PART_SPEECH.ADVERBS,
        'nouns': Icon.PART_SPEECH.NOUNS,
        'prepositions': Icon.PART_SPEECH.PREPOSITIONS,
        'punctuation': Icon.PART_SPEECH.PUNCTUATION,
        'verbs_2_part': Icon.PART_SPEECH.VERBS_2_PART,
        'verbs_modal': Icon.PART_SPEECH.VERBS_MODALS,
        'verbs_regular': Icon.PART_SPEECH.VERBS_REGULAR,
        'verbs_irregular': Icon.PART_SPEECH.VERBS_IRREGULAR,
    }
    TENSE_DICT = {
        Icon.TENSE.NONE: 'NONE',
        Icon.TENSE.PRESENT: 'present',
        Icon.TENSE.PRESENT_PARTICIPLE: 'present participle',
        Icon.TENSE.PAST: 'past',
        Icon.TENSE.PAST_PARTICIPLE: 'past participle',
    }

    @classmethod
    def __save(cls, filepath, word, descriptor, part_speech, tense):
        """
        Method to save icons to database and media store.
        """
        filename = filepath.split('/')[-1]
        with open(filepath, 'rb') as f:
            bytes_str = b''
            for buffer in iter(partial(f.read, Icon.BLOCK_SIZE), b''):
                bytes_str += buffer

            post_save.disconnect(Image.post_save, sender=Icon, dispatch_uid='0')

            icon = Icon.objects.create(
                word=word,
                descriptor=descriptor,
                part_speech=part_speech,
                tense=tense)
            icon.image.save(filename, ContentFile(bytes_str), save=False)

            post_save.connect(Image.post_save, sender=Icon, dispatch_uid='0')
            icon.save()

    @classmethod
    def __parse_filename(cls, part_speech, filename):
        """
        Method to obtain a word and a descriptor from a filename.
        """
        if filename[-4:].lower() == '.gif':
            filename = filename[:-4]

        filename_list = list(
            filter(lambda x: x != '', re.split(r'[ _]', filename)))

        if part_speech == 'verbs_2_part':
            word = filename_list[0]
            descriptor = ' '.join(filename_list[1:])
        elif part_speech == 'verbs_irregular':
            tense_dict = {
                '1': Icon.TENSE.PRESENT,
                'c': Icon.TENSE.PRESENT_PARTICIPLE,
                'p': Icon.TENSE.PAST,
                'pp': Icon.TENSE.PAST_PARTICIPLE,
            }

            try:
                tense = tense_dict[filename_list[0]]
            except KeyError:
                tense = Icon.TENSE.NONE
            except IndexError:
                raise CommandError('Invalid filename.')

            word = filename_list[1]
            descriptor = ' '.join(filename_list[2:])

            return word, descriptor, tense
        elif part_speech in cls.PART_SPEECH_DICT.keys():
            word = filename_list[0]
            descriptor = ' '.join(filename_list[1:])
        else:
            raise CommandError('Invalid part of speech.')

        return word, descriptor, Icon.TENSE.NONE

    @classmethod
    def __upload(cls, part_speech, directory):
        """
        Method to save adjective icons in a local directory to the database and media store.
        """
        for filename in os.listdir(directory):
            word, descriptor, tense = cls.__parse_filename(
                part_speech, filename)

            print('%05d' % cls.COUNT, filename)
            print('      tense: %s' % cls.TENSE_DICT[tense])
            print('      part of speech: %s' % part_speech)
            print(
                '      word: %s, descriptor: %s' %
                (word, descriptor if descriptor else 'NONE'))

            cls.__save(
                os.path.join(directory, filename), word, descriptor,
                cls.PART_SPEECH_DICT[part_speech], tense)
            cls.COUNT += 1

    @classmethod
    def upload(cls, part_speech, directory):
        """
        Wrapper method to save icons in a local directory to the database and media store.
        """
        if part_speech in {'adj', 'adjective'}:
            part_speech = 'adjectives'
        elif part_speech in {'adv', 'adverb'}:
            part_speech = 'adverbs'
        elif part_speech in {'conn', 'connective'}:
            part_speech = 'connectives'
        elif part_speech in {'n', 'noun'}:
            part_speech = 'nouns'
        elif part_speech in {'prep', 'preposition'}:
            part_speech = 'prepositions'
        elif part_speech == 'punc':
            part_speech = 'punctuation'
        elif part_speech in {'v2', 'verb_2_part'}:
            part_speech = 'verbs_2_part'
        elif part_speech in {'vi', 'verb_irregular'}:
            part_speech = 'verbs_irregular'
        elif part_speech in {'vm', 'verb_modals'}:
            part_speech = 'verbs_modal'
        elif part_speech in {'vr', 'verb_regular'}:
            part_speech = 'verbs_regular'

        if part_speech in cls.PART_SPEECH_DICT.keys():
            cls.__upload(part_speech, directory)
        else:
            raise CommandError('Invalid part of speech.')
