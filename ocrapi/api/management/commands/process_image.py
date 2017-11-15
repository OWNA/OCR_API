from django.core.management.base import BaseCommand, CommandError
from ocrapi.api.tasks import process_image


class Command(BaseCommand):
    help = 'Processes an image pending completion'

    def add_arguments(self, parser):
        parser.add_argument('image_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for image_id in options['image_id']:
            process_image(image_id)
