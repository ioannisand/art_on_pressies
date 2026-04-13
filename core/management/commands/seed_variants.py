"""Deprecated — variant seeding is now part of seed_demo."""
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Deprecated: use seed_demo instead'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING(
            'seed_variants is deprecated. Running seed_demo instead.'
        ))
        call_command('seed_demo')
