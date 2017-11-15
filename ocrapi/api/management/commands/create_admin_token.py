from django.core.management.base import BaseCommand, CommandError
from ocrapi.api.tasks import process_image
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create Admin credentials'

    def add_arguments(self, parser):
        parser.add_argument('password', type=str)

    def handle(self, *args, **options):
        print 'Creating admin with password %s' % options['password']
        admin = User.objects.create_superuser(
            username='admin', password=options['password'], email='')
        token = Token.objects.create(user=admin)
        print token.key
