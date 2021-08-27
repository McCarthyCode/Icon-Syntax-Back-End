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
    def __save(cls, filepath, word, descriptor, category):
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
                word=word, descriptor=descriptor, category=category)
            icon.image.save(filename, ContentFile(bytes_str), save=False)

            post_save.connect(Image.post_save, sender=Icon, dispatch_uid='0')
            icon.save()

    @classmethod
    def __parse_filename(cls, filename):
        """
        Method to obtain a word and a descriptor from a filename.
        """
        if filename[-4:].lower() != '.gif':
            raise CommandError(
                _('All files uploaded must have a ".gif" extension.'))

        filename = filename[:-4].replace('_', ' ')
        filename_list = list(
            filter(lambda x: x != '', [x.strip() for x in filename.split(',')]))

        word = filename_list[0]
        descriptor = ', '.join(filename_list[1:])

        return word, descriptor

    @classmethod
    def __upload(cls, directory, category):
        """
        Method to save adjective icons in a local directory to the database and media store.
        """
        print(directory)
        for filename in os.listdir(directory):
            word, descriptor = cls.__parse_filename(filename)

            cls.__save(
                os.path.join(directory, filename), word, descriptor, category)
            cls.COUNT += 1

    @classmethod
    def upload(cls, directory):
        """
        Wrapper method to save icons in a local directory to the database and media store.
        """
        # I
        adj = Category.objects.get_or_create(name=_('Adjectives'))[0]

        # I.A
        generic = Category.objects.get_or_create(
            name=_('Generic'), parent=adj)[0]
        cls.__upload(os.path.join(directory, 'Adjectives/Generic'), generic)

        # II
        adv = Category.objects.get_or_create(name=_('Adverbs'))[0]

        # II.A
        how = Category.objects.get_or_create(name=_('How'), parent=adv)[0]
        cls.__upload(os.path.join(directory, 'Adverbs/How'), how)

        how_much = Category.objects.get_or_create(
            name=_('How Much'), parent=adv)[0]
        cls.__upload(os.path.join(directory, 'Adverbs/How Much'), how_much)

        when = Category.objects.get_or_create(name=_('When'), parent=adv)[0]
        cls.__upload(os.path.join(directory, 'Adverbs/When'), when)

        where = Category.objects.get_or_create(name=_('Where'), parent=adv)[0]
        cls.__upload(os.path.join(directory, 'Adverbs/Where'), where)

        # III
        nouns = Category.objects.get_or_create(name=_('Nouns'))[0]

        # III.A
        culture = Category.objects.get_or_create(
            name=_('Culture'), parent=nouns)[0]

        # III.A.1
        creating = Category.objects.get_or_create(
            name=_('Creating'), parent=culture)[0]

        craft = Category.objects.get_or_create(
            name=_('Craft'), parent=creating)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Creating/Craft'), craft)

        performance = Category.objects.get_or_create(
            name=_('Performance'), parent=creating)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Creating/Performance'),
            performance)

        visual_art = Category.objects.get_or_create(
            name=_('Visual Art'), parent=creating)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Creating/Visual Art'),
            visual_art)

        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=creating)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Creating/Negatives'),
            negatives)

        # III.A.2
        eating_drinking = Category.objects.get_or_create(
            name=_('Eating & Drinking'), parent=culture)[0]

        cook = Category.objects.get_or_create(
            name=_('Cook'), parent=eating_drinking)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Eating & Drinking/Cook'),
            cook)

        dairy = Category.objects.get_or_create(
            name=_('Dairy'), parent=eating_drinking)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Eating & Drinking/Dairy'),
            dairy)

        drinks = Category.objects.get_or_create(
            name=_('Drinks'), parent=eating_drinking)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Eating & Drinking/Drinks'),
            drinks)

        fruit = Category.objects.get_or_create(
            name=_('Fruit'), parent=eating_drinking)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Eating & Drinking/Fruit'),
            fruit)

        grains = Category.objects.get_or_create(
            name=_('Grains'), parent=eating_drinking)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Eating & Drinking/Grains'),
            grains)

        groceries = Category.objects.get_or_create(
            name=_('Groceries'), parent=eating_drinking)[0]
        cls.__upload(
            os.path.join(
                directory, 'Nouns/Culture/Eating & Drinking/Groceries'),
            groceries)

        meals = Category.objects.get_or_create(
            name=_('Meals'), parent=eating_drinking)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Eating & Drinking/Meals'),
            meals)

        meat_and_fish = Category.objects.get_or_create(
            name=_('Meat, Animals & Fish'), parent=eating_drinking)[0]
        cls.__upload(
            os.path.join(
                directory, 'Nouns/Culture/Eating & Drinking/Meat & Fish'),
            meat_and_fish)

        sweets = Category.objects.get_or_create(
            name=_('Sweets'), parent=eating_drinking)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Eating & Drinking/Sweets'),
            sweets)

        vegetables = Category.objects.get_or_create(
            name=_('Vegetables'), parent=eating_drinking)[0]
        cls.__upload(
            os.path.join(
                directory, 'Nouns/Culture/Eating & Drinking/Vegetables'),
            vegetables)

        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=eating_drinking)[0]
        cls.__upload(
            os.path.join(
                directory, 'Nouns/Culture/Eating & Drinking/Negatives'),
            negatives)

        # III.A.3
        feeling = Category.objects.get_or_create(
            name=_('Feeling'), parent=culture)[0]

        # III.A.3.a
        gestures = Category.objects.get_or_create(
            name=_('Gestures'), parent=feeling)[0]

        generic = Category.objects.get_or_create(
            name=_('Generic'), parent=feeling)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Feeling/Gestures/Generic'),
            generic)

        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=feeling)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Feeling/Gestures/Negatives'),
            negatives)

        # III.A.3.b
        hearts = Category.objects.get_or_create(
            name=_('Hearts'), parent=feeling)[0]

        generic = Category.objects.get_or_create(
            name=_('Generic'), parent=feeling)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Feeling/Hearts/Generic'),
            generic)

        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=feeling)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Feeling/Hearts/Negatives'),
            negatives)

        # III.A.3.a
        faces = Category.objects.get_or_create(
            name=_('Faces'), parent=feeling)[0]

        eyes = Category.objects.get_or_create(name=_('Eyes'), parent=faces)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Feeling/Faces/Eyes'), eyes)

        masks = Category.objects.get_or_create(name=_('Masks'), parent=faces)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Feeling/Faces/Masks'), masks)

        mouths = Category.objects.get_or_create(
            name=_('Mouths'), parent=faces)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Feeling/Faces/Mouths'),
            mouths)

        # III.A.4
        governing = Category.objects.get_or_create(
            name=_('Governing'), parent=culture)[0]

        law = Category.objects.get_or_create(name=_('Law'), parent=governing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Governing/Law'), law)

        politics = Category.objects.get_or_create(
            name=_('Politics'), parent=governing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Governing/Politics'),
            politics)

        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=governing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Governing/Negatives'),
            negatives)

        # III.A.5
        healing = Category.objects.get_or_create(
            name=_('Healing'), parent=culture)[0]

        health = Category.objects.get_or_create(
            name=_('Health'), parent=healing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Healing/Health'), health)

        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=healing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Healing/Negatives'),
            negatives)

        # III.A.5.a
        body = Category.objects.get_or_create(name=_('Body'), parent=healing)[0]

        generic = Category.objects.get_or_create(
            name=_('Generic'), parent=body)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Healing/Body/Generic'),
            generic)

        death = Category.objects.get_or_create(name=_('Death'), parent=body)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Healing/Body/Death'), death)

        fitness = Category.objects.get_or_create(
            name=_('Fitness'), parent=body)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Healing/Body/Fitness'),
            fitness)

        pain = Category.objects.get_or_create(name=_('Pain'), parent=body)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Healing/Body/Pain'), pain)

        pregnancy = Category.objects.get_or_create(
            name=_('Pregnancy'), parent=body)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Healing/Body/Pregnancy'),
            pregnancy)

        senses = Category.objects.get_or_create(
            name=_('Senses'), parent=body)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Healing/Body/Senses'),
            senses)

        # III.A.6
        housing = Category.objects.get_or_create(
            name=_('Housing'), parent=culture)[0]

        infrastructure = Category.objects.get_or_create(
            name=_('Infrastructure'), parent=housing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Housing/Infrastructure'),
            infrastructure)

        interior = Category.objects.get_or_create(
            name=_('Interior'), parent=housing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Housing/Interior'), interior)

        landscape = Category.objects.get_or_create(
            name=_('Landscape'), parent=housing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Housing/Landscape'),
            landscape)

        public_buildings = Category.objects.get_or_create(
            name=_('Public Buildings'), parent=housing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Housing/Public Buildings'),
            public_buildings)

        types = Category.objects.get_or_create(
            name=_('Types'), parent=housing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Housing/Types'), types)

        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=housing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Housing/Negatives'),
            negatives)

        # III.A.6.a
        rooms = Category.objects.get_or_create(
            name=_('Rooms'), parent=housing)[0]

        basement = Category.objects.get_or_create(
            name=_('Basement'), parent=rooms)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Housing/Rooms/Basement'),
            basement)

        bathroom = Category.objects.get_or_create(
            name=_('Bathroom'), parent=rooms)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Housing/Rooms/Bathroom'),
            bathroom)

        bedroom = Category.objects.get_or_create(
            name=_('Bedroom'), parent=rooms)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Housing/Rooms/Bedroom'),
            bedroom)

        dining = Category.objects.get_or_create(
            name=_('Dining Room'), parent=rooms)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Housing/Rooms/Dining Room'),
            dining)

        kitchen = Category.objects.get_or_create(
            name=_('Kitchen'), parent=rooms)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Housing/Rooms/Kitchen'),
            kitchen)

        living = Category.objects.get_or_create(
            name=_('Living Room'), parent=rooms)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Housing/Rooms/Living Room'),
            living)

        nursery = Category.objects.get_or_create(
            name=_('Nursery'), parent=rooms)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Housing/Rooms/Nursery'),
            nursery)

        office = Category.objects.get_or_create(
            name=_('Office'), parent=rooms)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Housing/Rooms/Office'),
            office)

        # III.A.7
        learning = Category.objects.get_or_create(
            name=_('Learning'), parent=culture)[0]

        biology = Category.objects.get_or_create(
            name=_('Biology'), parent=learning)[0]

        animals = Category.objects.get_or_create(
            name=_('Animals'), parent=biology)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Learning/Biology/Animals'),
            animals)

        courses = Category.objects.get_or_create(
            name=_('Courses'), parent=learning)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Learning/Courses'), courses)

        nature = Category.objects.get_or_create(
            name=_('Nature'), parent=learning)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Learning/Nature'), nature)

        writing = Category.objects.get_or_create(
            name=_('Writing'), parent=learning)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Learning/Writing'), writing)

        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=learning)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Learning/Negatives'),
            negatives)

        # III.A.7.a
        math = Category.objects.get_or_create(
            name=_('Math'), parent=learning)[0]

        arithmetic = Category.objects.get_or_create(
            name=_('Arithmetic'), parent=math)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Learning/Math/Arithmetic'),
            arithmetic)

        counting = Category.objects.get_or_create(
            name=_('Counting'), parent=math)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Learning/Math/Counting'),
            counting)

        geometry = Category.objects.get_or_create(
            name=_('Geometry'), parent=math)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Learning/Math/Geometry'),
            geometry)

        measures = Category.objects.get_or_create(
            name=_('Measures'), parent=math)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Learning/Math/Measures'),
            measures)

        plot = Category.objects.get_or_create(name=_('Plot'), parent=math)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Learning/Math/Plot'), plot)

        # III.A.7.b
        reading = Category.objects.get_or_create(
            name=_('Reading'), parent=learning)[0]

        generic = Category.objects.get_or_create(
            name=_('Generic'), parent=reading)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Learning/Reading/Generic'),
            generic)

        negatives = Category.objects.get_or_create(
            name=_('Generic'), parent=learning)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Learning/Reading/Negatives'),
            negatives)

        # III.A.7.c
        school = Category.objects.get_or_create(
            name=_('School'), parent=learning)[0]
        generic = Category.objects.get_or_create(
            name=_('Generic'), parent=school)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Learning/School/Generic'),
            generic)
        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=learning)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Learning/School/Negatives'),
            negatives)

        # III.A.8
        playing = Category.objects.get_or_create(
            name=_('Playing'), parent=culture)[0]

        leisure = Category.objects.get_or_create(
            name=_('Leisure'), parent=playing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Playing/Leisure'), leisure)

        sports = Category.objects.get_or_create(
            name=_('Sports'), parent=playing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Playing/Sports'), sports)

        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=playing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Playing/Negatives'),
            negatives)

        # III.A.9
        praying = Category.objects.get_or_create(
            name=_('Praying'), parent=culture)[0]

        religion = Category.objects.get_or_create(
            name=_('Religion'), parent=praying)[0]

        generic = Category.objects.get_or_create(
            name=_('Generic'), parent=religion)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Praying/Religion/Generic'),
            generic)

        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=religion)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Praying/Religion/Negatives'),
            negatives)

        # III.A.10
        relating = Category.objects.get_or_create(
            name=_('Relating'), parent=culture)[0]

        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=relating)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Relating/Negatives'),
            negatives)

        # III.A.10.a
        adults = Category.objects.get_or_create(
            name=_('Adults'), parent=relating)[0]

        generic = Category.objects.get_or_create(
            name=_('Generic'), parent=adults)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Relating/Adults/Generic'),
            generic)

        pairs = Category.objects.get_or_create(
            name=_('People in Pairs'), parent=adults)[0]
        cls.__upload(
            os.path.join(
                directory, 'Nouns/Culture/Relating/Adults/People in Pairs'),
            pairs)

        pregnancy = Category.objects.get_or_create(
            name=_('Pregnancy'), parent=adults)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Relating/Adults/Pregnancy'),
            pregnancy)

        sex_play = Category.objects.get_or_create(
            name=_('Sex Play'), parent=adults)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Relating/Adults/Sex Play'),
            sex_play)

        single = Category.objects.get_or_create(
            name=_('Single Person'), parent=adults)[0]
        cls.__upload(
            os.path.join(
                directory, 'Nouns/Culture/Relating/Adults/Single Person'),
            single)

        # III.A.10.b
        children = Category.objects.get_or_create(
            name=_('Children'), parent=relating)[0]

        babies = Category.objects.get_or_create(
            name=_('Babies'), parent=children)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Relating/Children/Babies'),
            babies)

        minors = Category.objects.get_or_create(
            name=_('Minors'), parent=children)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Relating/Children/Minors'),
            minors)

        # III.A.10.b
        family = Category.objects.get_or_create(
            name=_('Family'), parent=relating)[0]

        extended = Category.objects.get_or_create(
            name=_('Extended'), parent=children)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Relating/Family/Extended'),
            extended)

        generations = Category.objects.get_or_create(
            name=_('Generations'), parent=children)[0]
        cls.__upload(
            os.path.join(
                directory, 'Nouns/Culture/Relating/Family/Generations'),
            generations)

        immediate = Category.objects.get_or_create(
            name=_('Immediate'), parent=children)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Relating/Family/Immediate'),
            immediate)

        pets = Category.objects.get_or_create(
            name=_('Pets'), parent=children)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Relating/Family/Pets'), pets)

        step = Category.objects.get_or_create(
            name=_('Step'), parent=children)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Relating/Family/Step'), step)

        # III.A.11
        speaking = Category.objects.get_or_create(
            name=_('Speaking'), parent=culture)[0]

        greetings = Category.objects.get_or_create(
            name=_('Greetings'), parent=speaking)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Speaking/Greetings'),
            greetings)

        voice = Category.objects.get_or_create(
            name=_('Voice'), parent=speaking)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Speaking/Voice'), voice)

        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=speaking)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Speaking/Negatives'),
            negatives)

        # III.A.12
        spending = Category.objects.get_or_create(
            name=_('Spending'), parent=culture)[0]

        money = Category.objects.get_or_create(
            name=_('Money'), parent=spending)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Spending/Money'), money)

        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=spending)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Spending/Negatives'),
            negatives)

        # III.A.13
        thinking = Category.objects.get_or_create(
            name=_('Thinking'), parent=culture)[0]

        mind = Category.objects.get_or_create(
            name=_('Mind'), parent=thinking)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Thinking/Mind'), mind)

        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=thinking)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Thinking/Negatives'),
            negatives)

        # III.A.14
        traveling = Category.objects.get_or_create(
            name=_('Traveling'), parent=culture)[0]

        directions_maps = Category.objects.get_or_create(
            name=_('Directions Maps'), parent=traveling)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Traveling/Directions Maps'),
            directions_maps)

        transportation = Category.objects.get_or_create(
            name=_('Transportation'), parent=traveling)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Traveling/Transportation'),
            transportation)

        vacation = Category.objects.get_or_create(
            name=_('Vacation Trip'), parent=traveling)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Traveling/Vacation Trip'),
            vacation)

        vehicle_upkeep = Category.objects.get_or_create(
            name=_('Vehicle Upkeep'), parent=traveling)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Traveling/Vehicle Upkeep'),
            vehicle_upkeep)

        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=traveling)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Traveling/Negatives'),
            negatives)

        # III.A.15
        wearing = Category.objects.get_or_create(
            name=_('Wearing'), parent=culture)[0]

        at_home = Category.objects.get_or_create(
            name=_('At Home'), parent=wearing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Wearing/At Home'), at_home)

        dress_up = Category.objects.get_or_create(
            name=_('Dress-Up'), parent=wearing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Wearing/Dress-Up'), dress_up)

        street_wear = Category.objects.get_or_create(
            name=_('Street Wear'), parent=wearing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Wearing/Street Wear'),
            street_wear)

        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=wearing)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Wearing/Negatives'),
            negatives)

        # III.A.16
        working = Category.objects.get_or_create(
            name=_('Working'), parent=culture)[0]

        jobs = Category.objects.get_or_create(name=_('Jobs'), parent=working)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Working/Jobs'), jobs)

        # III.A.16.a
        work = Category.objects.get_or_create(name=_('Work'), parent=working)[0]

        generic = Category.objects.get_or_create(
            name=_('Generic'), parent=work)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Working/Work/Generic'),
            generic)

        negatives = Category.objects.get_or_create(
            name=_('Negatives'), parent=working)[0]
        cls.__upload(
            os.path.join(directory, 'Nouns/Culture/Working/Work/Negatives'),
            work)

        # IV
        connectives = Category.objects.get_or_create(name=_('Connectives'))[0]
        cls.__upload(os.path.join(directory, 'Connectives'), connectives)

        # V
        counting = Category.objects.get_or_create(name=_('Counting'))[0]

        # V.A
        numbers = Category.objects.get_or_create(
            name=_('Numbers'), parent=counting)[0]

        cardinal = Category.objects.get_or_create(
            name=_('Cardinal'), parent=numbers)[0]
        cls.__upload(
            os.path.join(directory, 'Counting/Numbers/Cardinal'), cardinal)

        fractional = Category.objects.get_or_create(
            name=_('Fractional'), parent=numbers)[0]
        cls.__upload(
            os.path.join(directory, 'Counting/Numbers/Fractional'), fractional)

        ordinal = Category.objects.get_or_create(
            name=_('Ordinal'), parent=numbers)[0]
        cls.__upload(
            os.path.join(directory, 'Counting/Numbers/Ordinal'), ordinal)

        # V.B
        time = Category.objects.get_or_create(
            name=_('Time'), parent=counting)[0]

        analog = Category.objects.get_or_create(
            name=_('Analog'), parent=time)[0]
        cls.__upload(os.path.join(directory, 'Counting/Time/Analog'), analog)

        calendar = Category.objects.get_or_create(
            name=_('Calendar'), parent=time)[0]
        cls.__upload(
            os.path.join(directory, 'Counting/Time/Calendar'), calendar)

        day_night = Category.objects.get_or_create(
            name=_('Day & Night'), parent=time)[0]
        cls.__upload(
            os.path.join(directory, 'Counting/Time/Day & Night'), day_night)

        digital = Category.objects.get_or_create(
            name=_('Digital'), parent=time)[0]
        cls.__upload(os.path.join(directory, 'Counting/Time/Digital'), digital)

        hours = Category.objects.get_or_create(name=_('Hours'), parent=time)[0]
        cls.__upload(os.path.join(directory, 'Counting/Time/Hours'), hours)

        weekdays = Category.objects.get_or_create(
            name=_('Weekdays'), parent=time)[0]
        cls.__upload(
            os.path.join(directory, 'Counting/Time/Weekdays'), weekdays)

        # VI
        prepositions = Category.objects.get_or_create(name=_('Prepositions'))[0]
        cls.__upload(os.path.join(directory, 'Prepositions'), prepositions)

        # VII
        pronouns = Category.objects.get_or_create(name=_('Pronouns'))[0]

        contractions = Category.objects.get_or_create(
            name=_('Contractions'), parent=pronouns)[0]
        cls.__upload(
            os.path.join(directory, 'Pronouns/Contractions'), contractions)

        indefinite = Category.objects.get_or_create(
            name=_('Indefinite'), parent=pronouns)[0]
        cls.__upload(os.path.join(directory, 'Pronouns/Indefinite'), indefinite)

        personal = Category.objects.get_or_create(
            name=_('Personal'), parent=pronouns)[0]
        cls.__upload(os.path.join(directory, 'Pronouns/Personal'), personal)

        # VIII
        punctuation = Category.objects.get_or_create(name=_('Punctuation'))[0]
        cls.__upload(os.path.join(directory, 'Pronouns/Personal'), personal)

        # IX
        verbs = Category.objects.get_or_create(name=_('Verbs'))[0]

        modals = Category.objects.get_or_create(
            name=_('Modal Verbs'), parent=verbs)[0]
        cls.__upload(os.path.join(directory, 'Verbs/Modal Verbs'), modals)

        phrasal = Category.objects.get_or_create(
            name=_('Phrasal Verbs'), parent=verbs)[0]
        cls.__upload(os.path.join(directory, 'Verbs/Phrasal Verbs'), phrasal)

        regular = Category.objects.get_or_create(
            name=_('Regular Verbs'), parent=verbs)[0]
        cls.__upload(os.path.join(directory, 'Verbs/Regular Verbs'), regular)

        # IX.A
        iv = Category.objects.get_or_create(
            name=_('Irregular Verbs'), parent=verbs)[0]

        iv_past = Category.objects.get_or_create(
            name=_('Past Tense'), parent=iv)[0]
        cls.__upload(
            os.path.join(directory, 'Verbs/Irregular Verbs/Past Tense'),
            regular)

        iv_present = Category.objects.get_or_create(
            name=_('Present Tense'), parent=iv)[0]
        cls.__upload(
            os.path.join(directory, 'Verbs/Irregular Verbs/Present Tense'),
            regular)

        # X
        colors = Category.objects.get_or_create(name=_('Colors'))[0]
        cls.__upload(os.path.join(directory, 'Colors'), colors)

        # XI
        flags_languages = Category.objects.get_or_create(
            name=_('Flags & Languages'))[0]

        flags = Category.objects.get_or_create(
            name=_('Flags'), parent=flags_languages)[0]
        cls.__upload(os.path.join(directory, 'Flags & Languages/Flags'), flags)

        _global = Category.objects.get_or_create(
            name=_('Global Icons'), parent=flags_languages)[0]
        cls.__upload(
            os.path.join(directory, 'Flags & Languages/Global Icons'), _global)

        # XII
        titles_labels = Category.objects.get_or_create(
            name=_('Titles & Labels'))[0]
        cls.__upload(os.path.join(directory, 'Titles & Labels'), titles_labels)
