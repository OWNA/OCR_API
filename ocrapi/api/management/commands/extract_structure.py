from django.core.management.base import BaseCommand, CommandError
from ocrapi.api.tasks import extract_structure


class Command(BaseCommand):
    help = 'Extracts a structure pending completion'

    def add_arguments(self, parser):
        parser.add_argument('structure_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for structure_id in options['structure_id']:
            extract_structure(structure_id)
