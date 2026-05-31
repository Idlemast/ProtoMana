import subprocess
import sys
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Lance tailwind start + runserver dans un seul terminal'

    def add_arguments(self, parser):
        parser.add_argument('addrport', nargs='?', default='8000')

    def handle(self, *args, **options):
        tailwind_proc = subprocess.Popen([sys.executable, 'manage.py', 'tailwind', 'start'])
        try:
            call_command('runserver', options['addrport'])
        finally:
            tailwind_proc.terminate()
            tailwind_proc.wait()
