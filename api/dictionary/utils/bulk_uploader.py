import os
import re
import string

from functools import partial

from django.core.files.base import ContentFile
from django.core.management.base import CommandError
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from ..models import Word, Image, Icon, Category


class BulkUploader:
    """
    Class defining a utility method for uploading multiple icons.
    """
    COUNT = 1

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

        if part_speech == 'verb_2_part':
            word = filename_list[0]
            descriptor = ' '.join(filename_list[1:])
        elif part_speech == 'verb_irregular':
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
        if part_speech in {'adj', 'adjectives'}:
            part_speech = 'adjective'
        elif part_speech in {'adv', 'adverbs'}:
            part_speech = 'adverb'
        elif part_speech in {'conn', 'connectives'}:
            part_speech = 'connective'
        elif part_speech in {'n', 'nouns'}:
            part_speech = 'noun'
        elif part_speech in {'prep', 'prepositions'}:
            part_speech = 'preposition'
        elif part_speech == 'punc':
            part_speech = 'punctuation'
        elif part_speech in {'v2', 'verbs_2_part'}:
            part_speech = 'verb_2_part'
        elif part_speech in {'vi', 'verbs_irregular'}:
            part_speech = 'verb_irregular'
        elif part_speech in {'vm', 'verbs_modals'}:
            part_speech = 'verb_modal'
        elif part_speech in {'vr', 'verbs_regular'}:
            part_speech = 'verb_regular'

        if part_speech in cls.PART_SPEECH_DICT.keys():
            cls.__upload(part_speech, directory)
        else:
            raise CommandError('Invalid part of speech.')

    @classmethod
    def define_categories(cls):
        # I
        adj, created = Category.objects.get_or_create(name=_('Adjectives'))

        # I.A
        az, created = Category.objects.get_or_create(name=_('A-Z'), parent=adj)
        colors, created = Category.objects.get_or_create(name=_('Colors'), parent=adj)
        flags_languages, created = Category.objects.get_or_create(
            name=_('Flags & Languages'), parent=adj)
        titles_languages, created = Category.objects.get_or_create(
            name=_('Titles & Labels'), parent=adj)

        # II
        adv, created = Category.objects.get_or_create(name=_('Adverbs'))

        # II.A
        how, created = Category.objects.get_or_create(name=_('How'), parent=adv)
        how_much, created = Category.objects.get_or_create(
            name=_('How Much'), parent=adv)
        when, created = Category.objects.get_or_create(name=_('When'), parent=adv)
        where, created = Category.objects.get_or_create(name=_('Where'), parent=adv)

        # III
        nouns, created = Category.objects.get_or_create(name=_('Nouns'))

        # III.A
        culture, created = Category.objects.get_or_create(
            name=_('Culture'), parent=nouns)

        # III.A.1
        creating, created = Category.objects.get_or_create(
            name=_('Creating'), parent=culture)
        craft, created = Category.objects.get_or_create(
            name=_('Creating'), parent=creating)
        negatives, created = Category.objects.get_or_create(
            name=_('Negatives'), parent=creating)
        performance, created = Category.objects.get_or_create(
            name=_('Performance'), parent=creating)
        visual_art, created = Category.objects.get_or_create(
            name=_('Visual Art'), parent=creating)
        extras, created = Category.objects.get_or_create(
            name=_('Extras'), parent=creating)

        # III.A.2
        eating_drinking, created = Category.objects.get_or_create(
            name=_('Eating & Drinking'), parent=culture)
        cook, created = Category.objects.get_or_create(
            name=_('Cook'), parent=eating_drinking)
        dairy, created = Category.objects.get_or_create(
            name=_('Dairy'), parent=eating_drinking)
        drinks, created = Category.objects.get_or_create(
            name=_('Drinks'), parent=eating_drinking)
        feed_to, created = Category.objects.get_or_create(
            name=_('Feed to'), parent=eating_drinking)
        fruit, created = Category.objects.get_or_create(
            name=_('Fruit'), parent=eating_drinking)
        groceries, created = Category.objects.get_or_create(
            name=_('Groceries'), parent=eating_drinking)
        meals_at_home, created = Category.objects.get_or_create(
            name=_('Meals at Home'), parent=eating_drinking)
        meals_out, created = Category.objects.get_or_create(
            name=_('Meals out'), parent=eating_drinking)
        meat_animals_and_fish, created = Category.objects.get_or_create(
            name=_('Meat, Animals & Fish'), parent=eating_drinking)
        negatives, created = Category.objects.get_or_create(
            name=_('Negatives'), parent=eating_drinking)
        starch, created = Category.objects.get_or_create(
            name=_('Starch'), parent=eating_drinking)
        sweets, created = Category.objects.get_or_create(
            name=_('Sweets'), parent=eating_drinking)
        vegetables, created = Category.objects.get_or_create(
            name=_('Vegetables'), parent=eating_drinking)
        extras, created = Category.objects.get_or_create(
            name=_('Extras'), parent=eating_drinking)

        # III.A.3
        feeling, created = Category.objects.get_or_create(
            name=_('Feeling'), parent=culture)
        faces_eyes, created = Category.objects.get_or_create(
            name=_('Faces Eyes'), parent=feeling)
        faces_masks, created = Category.objects.get_or_create(
            name=_('Faces Masks'), parent=feeling)
        gestures, created = Category.objects.get_or_create(
            name=_('Gestures'), parent=feeling)
        hearts, created = Category.objects.get_or_create(
            name=_('Hearts'), parent=feeling)
        negatives, created = Category.objects.get_or_create(
            name=_('Negatives'), parent=feeling)
        gestures, created = Category.objects.get_or_create(
            name=_('Gestures'), parent=negatives)
        hearts, created = Category.objects.get_or_create(
            name=_('Hearts'), parent=feeling)
        extras, created = Category.objects.get_or_create(
            name=_('Extras'), parent=feeling)

        # III.A.4
        governing, created = Category.objects.get_or_create(
            name=_('Governing'), parent=culture)
        law, created = Category.objects.get_or_create(name=_('Law'), parent=governing)
        negatives, created = Category.objects.get_or_create(
            name=_('Negatives'), parent=governing)
        extras, created = Category.objects.get_or_create(
            name=_('Extras'), parent=governing)

        # III.A.5
        healing, created = Category.objects.get_or_create(
            name=_('Healing'), parent=culture)
        body, created = Category.objects.get_or_create(name=_('Body'), parent=healing)
        health, created = Category.objects.get_or_create(
            name=_('Health'), parent=healing)
        negatives, created = Category.objects.get_or_create(
            name=_('Negatives'), parent=healing)
        extras, created = Category.objects.get_or_create(
            name=_('Extras'), parent=healing)

        # III.A.6
        housing, created = Category.objects.get_or_create(
            name=_('Housing'), parent=culture)
        az, created = Category.objects.get_or_create(name=_('A-Z'), parent=housing)
        infrastructure, created = Category.objects.get_or_create(
            name=_('Infrastructure'), parent=housing)
        interior, created = Category.objects.get_or_create(
            name=_('Interior'), parent=housing)
        landscape, created = Category.objects.get_or_create(
            name=_('Landscape'), parent=housing)
        public_buildings, created = Category.objects.get_or_create(
            name=_('Public Buildings'), parent=housing)
        negatives, created = Category.objects.get_or_create(
            name=_('Negatives'), parent=housing)
        extras, created = Category.objects.get_or_create(
            name=_('Extras'), parent=housing)

        # III.A.6.a
        rooms, created = Category.objects.get_or_create(name=_('Rooms'), parent=housing)
        basement, created = Category.objects.get_or_create(
            name=_('Basement'), parent=rooms)
        bathroom, created = Category.objects.get_or_create(
            name=_('Bathroom'), parent=rooms)
        bedroom, created = Category.objects.get_or_create(
            name=_('Bedroom'), parent=rooms)
        dining, created = Category.objects.get_or_create(
            name=_('Dining Room'), parent=rooms)
        kitchen, created = Category.objects.get_or_create(
            name=_('Kitchen'), parent=rooms)
        living, created = Category.objects.get_or_create(
            name=_('Living Room'), parent=rooms)
        nursery, created = Category.objects.get_or_create(
            name=_('Nursery'), parent=rooms)
        office, created = Category.objects.get_or_create(name=_('Office'), parent=rooms)

        # III.A.7
        learning, created = Category.objects.get_or_create(
            name=_('Learning'), parent=culture)
        biology, created = Category.objects.get_or_create(
            name=_('Biology'), parent=learning)
        courses, created = Category.objects.get_or_create(
            name=_('Courses'), parent=learning)
        nature, created = Category.objects.get_or_create(
            name=_('Nature'), parent=learning)
        negatives, created = Category.objects.get_or_create(
            name=_('Negatives'), parent=learning)
        reading, created = Category.objects.get_or_create(
            name=_('Reading'), parent=learning)
        school, created = Category.objects.get_or_create(
            name=_('School'), parent=learning)
        writing, created = Category.objects.get_or_create(
            name=_('Writing'), parent=learning)

        # III.A.7.a
        math, created = Category.objects.get_or_create(name=_('Math'), parent=learning)
        counting, created = Category.objects.get_or_create(
            name=_('Counting'), parent=math)
        geometry, created = Category.objects.get_or_create(
            name=_('Geometry'), parent=math)
        measures, created = Category.objects.get_or_create(
            name=_('Measures'), parent=math)
        plot, created = Category.objects.get_or_create(name=_('Plot'), parent=math)
        symbols, created = Category.objects.get_or_create(name=_('Symbols'), parent=math)
        negatives, created = Category.objects.get_or_create(
            name=_('Negatives'), parent=math)

        # III.A.8
        playing, created = Category.objects.get_or_create(
            name=_('Playing'), parent=culture)
        leisure, created = Category.objects.get_or_create(
            name=_('Leisure'), parent=playing)
        sports, created = Category.objects.get_or_create(
            name=_('Sports'), parent=playing)
        extras, created = Category.objects.get_or_create(
            name=_('Extras'), parent=playing)
        negatives, created = Category.objects.get_or_create(
            name=_('Negatives'), parent=playing)

        # III.A.9
        praying, created = Category.objects.get_or_create(
            name=_('Praying'), parent=culture)
        religion, created = Category.objects.get_or_create(
            name=_('Religion'), parent=praying)
        extras, created = Category.objects.get_or_create(
            name=_('Extras'), parent=praying)
        negatives, created = Category.objects.get_or_create(
            name=_('Negatives'), parent=praying)

        # III.A.10
        relating, created = Category.objects.get_or_create(
            name=_('Relating'), parent=culture)
        adults, created = Category.objects.get_or_create(
            name=_('Adults'), parent=relating)
        children, created = Category.objects.get_or_create(
            name=_('Children'), parent=relating)
        adults, created = Category.objects.get_or_create(
            name=_('Adults'), parent=relating)
        extras, created = Category.objects.get_or_create(
            name=_('Extras'), parent=relating)
        negatives, created = Category.objects.get_or_create(
            name=_('Negatives'), parent=relating)

        # III.A.11
        speaking, created = Category.objects.get_or_create(
            name=_('Speaking'), parent=culture)
        greetings, created = Category.objects.get_or_create(
            name=_('Greetings'), parent=speaking)
        voice, created = Category.objects.get_or_create(name=_('Voice'), parent=speaking)
        extras, created = Category.objects.get_or_create(
            name=_('Extras'), parent=speaking)
        negatives, created = Category.objects.get_or_create(
            name=_('Negatives'), parent=speaking)

        # III.A.12
        spending, created = Category.objects.get_or_create(
            name=_('Spending'), parent=culture)
        money, created = Category.objects.get_or_create(name=_('Money'), parent=spending)
        extras, created = Category.objects.get_or_create(
            name=_('Extras'), parent=spending)
        negatives, created = Category.objects.get_or_create(
            name=_('Negatives'), parent=spending)

        # III.A.13
        thinking, created = Category.objects.get_or_create(
            name=_('Thinking'), parent=culture)
        Mind, created = Category.objects.get_or_create(name=_('Mind'), parent=thinking)
        _self, created = Category.objects.get_or_create(name=_('Self'), parent=thinking)
        extras, created = Category.objects.get_or_create(
            name=_('Extras'), parent=thinking)
        negatives, created = Category.objects.get_or_create(
            name=_('Negatives'), parent=thinking)

        # III.A.14
        traveling, created = Category.objects.get_or_create(
            name=_('Traveling'), parent=culture)
        directions_maps, created = Category.objects.get_or_create(
            name=_('Directions Maps'), parent=traveling)
        land_sea, created = Category.objects.get_or_create(
            name=_('Land & Sea'), parent=traveling)
        transportation, created = Category.objects.get_or_create(
            name=_('Transportation'), parent=traveling)
        trip_weather, created = Category.objects.get_or_create(
            name=_('Trip Weather'), parent=traveling)
        vacation, created = Category.objects.get_or_create(
            name=_('Vacation Trip'), parent=traveling)
        vehicle_upkeep, created = Category.objects.get_or_create(
            name=_('Vehicle Upkeep'), parent=traveling)
        extras, created = Category.objects.get_or_create(
            name=_('Extras'), parent=traveling)
        negatives, created = Category.objects.get_or_create(
            name=_('Negatives'), parent=traveling)

        # III.A.15
        wearing, created = Category.objects.get_or_create(
            name=_('Wearing'), parent=culture)
        at_home, created = Category.objects.get_or_create(
            name=_('At Home'), parent=wearing)
        dress_up, created = Category.objects.get_or_create(
            name=_('Dress-Up'), parent=wearing)
        street_wear, created = Category.objects.get_or_create(
            name=_('Street Wear'), parent=wearing)
        extras, created = Category.objects.get_or_create(
            name=_('Extras'), parent=wearing)

        # III.A.16
        working, created = Category.objects.get_or_create(
            name=_('Working'), parent=culture)
        work, created = Category.objects.get_or_create(name=_('Work'), parent=working)
        jobs, created = Category.objects.get_or_create(name=_('Jobs'), parent=working)
        extras, created = Category.objects.get_or_create(
            name=_('Extras'), parent=working)
        negatives, created = Category.objects.get_or_create(
            name=_('Negatives'), parent=working)

        # IV
        connectives, created = Category.objects.get_or_create(name=_('Connectives'))

        # V
        counting, created = Category.objects.get_or_create(name=_('Counting'))
        numbers, created = Category.objects.get_or_create(
            name=_('Numbers'), parent=counting)
        time, created = Category.objects.get_or_create(name=_('Time'), parent=counting)

        # VI
        prepositions, created = Category.objects.get_or_create(name=_('Prepositions'))

        # VII
        pronouns, created = Category.objects.get_or_create(name=_('Pronouns'))
        contractions, created = Category.objects.get_or_create(
            name=_('Contractions'), parent=pronouns)
        indefinite, created = Category.objects.get_or_create(
            name=_('Indefinite'), parent=pronouns)
        personal, created = Category.objects.get_or_create(
            name=_('Personal'), parent=pronouns)

        # VIII
        punctuation, created = Category.objects.get_or_create(name=_('Punctuation'))

        # IX
        verbs, created = Category.objects.get_or_create(name=_('Verbs'))
        iv, created = Category.objects.get_or_create(
            name=_('Irregular Verbs'), parent=verbs)
        iv_past, created = Category.objects.get_or_create(
            name=_('Past Tense'), parent=iv)
        iv_present, created = Category.objects.get_or_create(
            name=_('Present Tense'), parent=iv)
        modals, created = Category.objects.get_or_create(
            name=_('Modal Verbs'), parent=verbs)
        phrasal, created = Category.objects.get_or_create(
            name=_('Phrasal Verbs'), parent=verbs)
        regular, created = Category.objects.get_or_create(
            name=_('Regular Verbs'), parent=verbs)
