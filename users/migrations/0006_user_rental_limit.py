# Generated by Django 3.2 on 2021-04-27 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_auto_20210421_1311"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="rental_limit",
            field=models.PositiveSmallIntegerField(default=4),
        ),
    ]
