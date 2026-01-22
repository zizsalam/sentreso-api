"""
Management command to create a Master with API key.
"""

from django.core.management.base import BaseCommand
from apps.masters.models import Master


class Command(BaseCommand):
    help = 'Create a new Master with auto-generated API key'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            default='Test Master',
            help='Master name'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='test@sentreso.com',
            help='Master email'
        )

    def handle(self, *args, **options):
        name = options['name']
        email = options['email']

        try:
            master = Master.objects.create(name=name, email=email)
            self.stdout.write(self.style.SUCCESS('\nMaster created successfully!\n'))
            self.stdout.write(f'Name: {master.name}')
            self.stdout.write(f'Email: {master.email}')
            self.stdout.write(self.style.WARNING('\nAPI Key (save this!):'))
            self.stdout.write(self.style.SUCCESS(f'{master.api_key}\n'))
            self.stdout.write('Use this API key to login to admin UI at: /admin-ui/login/\n')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating master: {e}'))

