# Generated by Django 4.2.5 on 2023-12-13 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("course", "0007_remove_course_semester_remove_course_year_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="vertical",
            field=models.CharField(
                choices=[("Unit", "Unit"), ("Branch", "Branch")],
                max_length=25,
                null=True,
            ),
        ),
    ]
