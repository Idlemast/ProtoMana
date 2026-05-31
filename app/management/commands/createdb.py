import pymysql
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Crée la base de données MySQL puis applique les migrations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-migrate', action='store_true',
            help='Crée la base sans appliquer les migrations'
        )
        parser.add_argument(
            '--drop', action='store_true',
            help='Supprime la base existante avant de la recréer'
        )

    def handle(self, *args, **options):
        db = settings.DATABASES['default']
        name = db['NAME']

        conn = pymysql.connect(
            host=db['HOST'],
            port=int(db['PORT']),
            user=db['USER'],
            password=db['PASSWORD'],
            charset='utf8mb4',
        )
        try:
            with conn.cursor() as cursor:
                if options['drop']:
                    cursor.execute(f"DROP DATABASE IF EXISTS `{name}`;")
                    self.stdout.write(self.style.WARNING(f'✘ Base "{name}" supprimée.'))
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{name}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                )
            self.stdout.write(self.style.SUCCESS(f'✔ Base "{name}" créée.'))
        finally:
            conn.close()

        if not options['no_migrate']:
            self.stdout.write('Applying migrations...')
            call_command('migrate')
