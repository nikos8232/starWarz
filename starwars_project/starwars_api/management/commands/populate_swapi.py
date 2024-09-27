from django.core.management.base import BaseCommand

from starwars_api.services.fetch_and_store_data import fetch_and_store_data


class Command(BaseCommand):
    help = 'Fetch and store data from SWAPI'

    def handle(self, *args, **kwargs):
        fetch_and_store_data()
        self.stdout.write(self.style.SUCCESS('Data fetched and stored successfully.'))