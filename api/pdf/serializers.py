import re
from collections import OrderedDict

from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.pdf.models import PDF


class PDFSerializer(serializers.ModelSerializer):
    pdf = serializers.FileField()
    categories = serializers.CharField(max_length=160)

    class Meta:
        model = PDF
        fields = ['id', 'title', 'categories', 'topic', 'pdf', 'md5']
        read_only_fields = ['id', 'md5']

    def validate_categories(self, categories_str):
        if not re.match(r'[a-zA-Z0-9 ,]+', categories_str):
            raise ValidationError(
                _(
                    'The categories list may only contain letters, digits, and spaces separated by commas.'
                ),
                'invalid_str',
            )

        categories_set = set(
            filter(lambda x: len(x) > 0, categories_str.split(',')))

        if categories_set == set({}):
            raise ValidationError(
                _('The categories list must contain at least one category.'),
                'invalid_cat',
            )

        return categories_str

    def create(self, validated_data):
        kwargs = dict(validated_data)  # use dict typecast for a deep copy
        kwargs.pop('categories')

        obj = PDF.objects.create(**kwargs)

        categories_set = set(
            filter(
                lambda x: len(x) > 0, validated_data['categories'].split(',')))

        for category_str in categories_set:
            category, created = PDF.Category.objects.get_or_create(
                name=category_str)
            obj.categories.add(category)

        return obj

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.topic = validated_data.get('topic', instance.topic)

        categories = validated_data.get('categories', instance.categories or '')
        categories = categories.split(',')

        # add new categories and delete orphaned ones
        del_set = set(
            map(
                lambda x: x.name,
                self.instance.categories.filter(pdf=instance.id)))

        for name in categories:
            category, created = PDF.Category.objects.get_or_create(name=name)
            self.instance.categories.add(category)

            del_set.discard(name)

        for name in del_set:
            if PDF.objects.filter(categories__name=name).count() == 1:
                PDF.Category.objects.filter(name=name).delete()
            else:
                self.instance.categories.remove(
                    PDF.Category.objects.get(name=name))

        instance.save()

        return instance

    @property
    def data(self):
        return self.instance.obj


class PDFCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = PDF.Category
        fields = '__all__'
