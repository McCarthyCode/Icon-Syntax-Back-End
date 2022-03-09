import re
from collections import OrderedDict

from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.pdf.models import PDF


class PDFSerializer(serializers.ModelSerializer):
    pdf = serializers.FileField()
    categories = serializers.CharField(max_length=80)

    class Meta:
        model = PDF
        fields = ['id', 'title', 'categories', 'pdf', 'md5']
        read_only_fields = ['id', 'md5']

    def validate_categories(self, categories_str):
        if not re.match(r'[a-zA-Z0-9 ,]+', categories_str):
            raise ValidationError(
                _(
                    'The categories list may only contain letters, digits, and spaces.'
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

        # original_obj_set = self.instance.categories_set \
        #     if self.instance else set({})
        # updated_obj_set = set({})

        # for category_str in categories_set:
        #     updated_obj_set.add(
        #         PDF.Category.objects.get_or_create(name=category_str))

        # for category_obj in original_obj_set - updated_obj_set:
        #     if PDF.Category.objects.filter(name=category_obj.name).count() == 1:
        #         category_obj.delete()

        return categories_str

    def create(self, validated_data):
        kwargs = dict(validated_data)
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

    @property
    def data(self):
        categories_str = ','.join(
            map(lambda x: x['name'], self.instance.categories.values('name')))

        return OrderedDict(
            {
                'id': self.instance.id,
                'categories': categories_str,
                'title': self.instance.title,
                'pdf': self.instance.pdf.name,
                'md5': self.instance.md5
            })


class PDFCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = PDF.Category
        fields = '__all__'