# Generated by Django 3.2 on 2021-04-24 08:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("bikes", "0008_alter_bike_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="reservation",
            name="user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reservations",
                to="users.user",
            ),
            preserve_default=False,
        ),
    ]
