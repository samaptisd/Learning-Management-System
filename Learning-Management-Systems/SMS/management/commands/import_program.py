import csv
from django.core.management.base import BaseCommand
from django.db import transaction
import os
from django.core.management.base import BaseCommand
from course.models import Course
from course.models import Course

print("Current Working Directory:", os.getcwd())


class Command(BaseCommand):
    help = 'Import users from CSV file'

    def handle(self, *args, **options):
        file_path = 'course.csv'  # Update with your file name
        print(file_path)
        print("Resolved File Path:", os.path.abspath(file_path))

        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            # Use a transaction to ensure atomicity

            with transaction.atomic():
                for row in reader:
                    Course.objects.create(
                        slug=row['slug'],
                        title=row['title'],
                        code=row['code'],
                        credit=row['credit'],
                        summary=row['summary'],
                        program_Id=row['program_Id'],
                        level=row['level'],
                        vertical=row['vertical'],
                        language=row['language'],
                        is_elective=row['is_elective'],
                    )


                    self.stdout.write(self.style.SUCCESS(f'Successfully imported program: {"program_id"}'))

                self.stdout.write(self.style.SUCCESS('Import process completed'))





