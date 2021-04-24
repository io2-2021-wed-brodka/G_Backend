# Generated by Django 3.2 on 2021-04-20 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_user_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="state",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "Active"), (1, "Banned")], default=0
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "User"), (1, "Tech"), (2, "Admin")], default=0
            ),
        ),
    ]
