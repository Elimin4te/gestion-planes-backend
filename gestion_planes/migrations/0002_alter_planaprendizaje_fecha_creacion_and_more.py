# Generated by Django 5.1.6 on 2025-02-20 05:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gestion_planes", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="planaprendizaje",
            name="fecha_creacion",
            field=models.DateTimeField(
                default=datetime.datetime(2025, 2, 20, 5, 32, 12, 492180)
            ),
        ),
        migrations.AlterField(
            model_name="planevaluacion",
            name="fecha_creacion",
            field=models.DateTimeField(
                default=datetime.datetime(2025, 2, 20, 5, 32, 12, 493976)
            ),
        ),
    ]
