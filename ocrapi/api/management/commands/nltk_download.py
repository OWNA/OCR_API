from django.core.management.base import BaseCommand, CommandError
import nltk

class Command(BaseCommand):
    help = 'Download stop words'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        nltk.download('stopwords')
        nltk.download('punkt')
        nltk.download('wordnet')
