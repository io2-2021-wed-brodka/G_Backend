# Generated by Django 3.2 on 2021-04-21 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_auto_20210420_2014"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[("user", "User"), ("tech", "Tech"), ("admin", "Admin")],
                default="user",
                max_length=5,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="state",
            field=models.CharField(
                choices=[("active", "Active"), ("blocked", "Blocked")],
                default="active",
                max_length=7,
            ),
        ),
    ]
