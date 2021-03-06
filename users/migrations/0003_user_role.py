# Generated by Django 3.2 on 2021-04-13 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_auto_20210406_1328"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[("user", "User"), ("tech", "Tech"), ("admin", "Admin")],
                default="user",
                max_length=32,
            ),
            preserve_default=False,
        ),
    ]
