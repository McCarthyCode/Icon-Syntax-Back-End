import hashlib
import os

from base64 import b16encode, b64encode
from collections import OrderedDict
from functools import partial
from io import BytesIO
from PIL import Image

from django.conf import settings
from django.db import models
from django.db.utils import IntegrityError
from django.db.models.signals import post_save
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from api.models import TimestampedModel

from api.models import TimestampedModel
from api.dictionary.utils import Base64Converter


class PDF(TimestampedModel):
    """
    A model storing a PDF, its title, and its Bookshelf category.
    """

    class Category(TimestampedModel):
        """
        A model storing a categorical name.
        """
        name = models.CharField(_('Name'), max_length=40, unique=True)

    # Static variables
    RELATIVE_PATH = 'pdf'
    BLOCK_SIZE = 2**16

    # Attributes
    title = models.CharField(_('Title'), max_length=80)
    pdf = models.FileField(_('PDF'), upload_to=RELATIVE_PATH, max_length=160)
    categories = models.ManyToManyField(Category, related_name=_('Category'))
    _hash = models.BinaryField(_('MD5 hash'), null=True, max_length=16)

    def __str__(self):
        """
        The value of the class instance when typecast as a string.
        """
        return self.title

    def __hash(self):
        """
        Create a MD5 cryptographic hash of the PDF, store it in the database, and rename the file.
        """
        hasher = hashlib.md5()
        filename = os.path.join(settings.MEDIA_ROOT, self.pdf.name)

        with open(filename, 'rb') as pdf:
            for buffer in iter(partial(pdf.read, self.BLOCK_SIZE), b''):
                hasher.update(buffer)

            # Make changes if stored hash does not exist
            if not self._hash or self._hash != hasher.hexdigest().lower():
                # Update hash and PDF name attributes
                self._hash = hasher.digest()
                self.pdf.name = os.path.join(
                    self.RELATIVE_PATH,
                    hasher.hexdigest().lower() + '.pdf')

                # Save
                post_save.disconnect(
                    PDF.post_save, sender=PDF, dispatch_uid='3')

                self.save()

                post_save.connect(PDF.post_save, sender=PDF, dispatch_uid='3')

                # Update filesystem
                new_filename = os.path.join(settings.MEDIA_ROOT, self.pdf.name)
                os.rename(filename, new_filename)

    def delete(self):
        """
        Delete the file before deleting the model instance.
        """
        self.pdf.delete()
        super().delete()

    def add_category(self, name):
        category = Category.objects.get_or_create(name=name)

        if category not in self.category_set:
            try:
                self.categories_set.add(category)
            except IntegrityError:
                pass

    def rename_category(self, old_name, new_name):
        old_category = get_object_or_404(Category, name=old_name)
        new_category = Category.objects.get_or_create(name=new_name)

        for pdf in category.pdfs_set:
            pdf.categories_set.remove(old_category)
            pdf.categories_set.add(new_category)

        old_category.delete()

    def remove_category(self, name):
        category = get_object_or_404(Category, name=name)

        if category in self.category_set:
            self.categories_set.remove(category)

            if len(category.pdfs_set) == 0:
                category.delete()

    @property
    def md5(self):
        """
        Get the MD5 PDF hash as a base-16 string.
        """
        return str(
            b16encode(self._hash).lower(), 'utf-8') if self._hash else None

    @property
    def obj(self):
        """
        Serialize relevant fields and properties for JSON output.
        """
        return OrderedDict(
            {
                'id': self.id,
                'title': self.title,
                'pdf': self.pdf.url,
                'md5': self.md5,
            })

    @classmethod
    def post_save(
            cls, sender, instance, created, raw, using, update_fields,
            **kwargs):
        """
        Method to perform preliminary operations just after instance creation.
        """
        if instance.pdf:
            instance.__hash()


post_save.connect(PDF.post_save, sender=PDF, dispatch_uid='3')
