import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction
import os
from accounts.models import User


print("Current Working Directory:", os.getcwd())

class Command(BaseCommand):
    help = 'Import users from CSV file'

    def handle(self, *args, **options):
        file_path = r'Password_Generate.csv'  # Update with your file name
        print(file_path)
        print("Resolved File Path:", os.path.abspath(file_path))

        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            # Use a transaction to ensure atomicity
            with transaction.atomic():
                for row in reader:
                    # Assuming your CSV has headers: 'username', 'email', 'password', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_student', 'is_lecturer', 'phone', 'address', 'picture', 'is_parent', 'is_dep_head'
                    username = row['username']
                    email = row['email']
                    password = make_password(row['password'])

                    # Create user and save to the database
                    User.objects.create(
                        username=username,
                        email=email,
                        password=password,
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        is_staff=row['is_staff'].lower() == 'true',
                        is_active=row['is_active'].lower() == 'true',
                        is_student=row['is_student'].lower() == 'true',
                        is_lecturer=row['is_lecturer'].lower() == 'true',
                        phone=row['phone'],
                        address=row['address'],
                        picture=row['picture'],
                        is_parent=row['is_parent'].lower() == 'true',
                        is_dep_head=row['is_dep_head'].lower() == 'true'
                    )

                    self.stdout.write(self.style.SUCCESS(f'Successfully imported user: {username}'))

                self.stdout.write(self.style.SUCCESS('Import process completed'))
