# Generated by Django 4.2.5 on 2024-02-08 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quiz", "0008_alter_sitting_user_answers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitting",
            name="user_answers",
            field=models.TextField(
                blank=True, default="{}", max_length=1024, verbose_name="User Answers"
            ),
        ),
    ]
