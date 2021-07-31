from django.core.management.base import BaseCommand, CommandError
from api.dictionary.utils.bulk_uploader import BulkUploader


class Command(BaseCommand):
    help = 'Uploads icons in a given directory based on its part of speech format.'

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str)

    def handle(self, *args, **options):
        BulkUploader.upload(options['directory'])

        self.stdout.write(self.style.SUCCESS('Upload successful.'))
