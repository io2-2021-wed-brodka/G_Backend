# Generated by Django 3.1.7 on 2021-03-17 12:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("stations", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Bike",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "state",
                    models.CharField(
                        choices=[("working", "Working"), ("in_service", "In service"), ("blocked", "Blocked")],
                        default="working",
                        max_length=20,
                    ),
                ),
                (
                    "station",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="stations.station"
                    ),
                ),
            ],
        ),
    ]
