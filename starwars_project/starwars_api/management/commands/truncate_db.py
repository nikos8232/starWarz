from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection

class Command(BaseCommand):
    help = 'Truncate all tables in the database'

    def handle(self, *args, **kwargs):
        # Get all models
        all_models = apps.get_models()

        with connection.cursor() as cursor:
            # Disable foreign key checks
            cursor.execute('PRAGMA foreign_keys = OFF;')
            try:
                for model in all_models:
                    # Delete all records from the table
                    cursor.execute(f'DELETE FROM {model._meta.db_table};')
                    # Reset the auto-increment id if applicable
                    cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{model._meta.db_table}";')
            finally:
                # Re-enable foreign key checks
                cursor.execute('PRAGMA foreign_keys = ON;')

        self.stdout.write(self.style.SUCCESS('Successfully truncated all tables.'))
