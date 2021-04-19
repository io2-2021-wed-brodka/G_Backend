# Generated by Django 3.2 on 2021-04-15 19:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("stations", "0003_auto_20210406_1319"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("bikes", "0005_auto_20210415_1917"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bike",
            name="station",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="bikes",
                to="stations.station",
            ),
        ),
        migrations.AlterField(
            model_name="bike",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bikes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]