import csv
import os
import django
import gspread
from django.core.management.base import BaseCommand
from accounts.models import User
from django.contrib.auth.hashers import make_password
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SMS.settings")
django.setup()




class Command(BaseCommand):
    help = 'Import user data from Google Sheet'

    def handle(self, *args, **options):
        # Add your Google Sheets credentials JSON file
        gc = gspread.service_account(filename='credentials.json')

        # Open the Google Sheet by title or URL
        sheet = gc.open('https://docs.google.com/spreadsheets/d/1BX_v1Jrfi0ukbREE6i2pVLA6aNr4uAwASSINyoPRiM8/edit#gid=854627987').sheet1

        # Get all values from the Google Sheet
        data = sheet.get_all_values()

        # Skip the header row if it exists
        header = data[0] if data else []
        rows = data[1:] if data else []

        # Prepare data for bulk insertion
        user_objects = []
        for row in rows:
            # Assuming the order of columns in the sheet matches the order of fields in your User model
            user_data = dict(zip(header, row))

            # Hash the password
            user_data['password'] = make_password(user_data['password'])

            # Create a User object
            user_objects.append(User(**user_data))

        # Bulk insert the data into the database
        User.objects.bulk_create(user_objects, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f'Successfully added {len(user_objects)} users'))
