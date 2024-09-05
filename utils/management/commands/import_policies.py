from django.core.management.base import BaseCommand
from utils.import_policy_csv import import_data

class Command(BaseCommand):
    help = 'Imports policies from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_filepath', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_filepath = options['csv_filepath']
        import_data(csv_filepath)
        self.stdout.write(self.style.SUCCESS('Successfully imported policies'))
