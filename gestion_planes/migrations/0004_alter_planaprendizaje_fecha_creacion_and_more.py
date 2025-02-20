# Generated by Django 5.1.6 on 2025-02-20 05:33

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gestion_planes", "0003_alter_planaprendizaje_fecha_creacion_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="planaprendizaje",
            name="fecha_creacion",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="planevaluacion",
            name="fecha_creacion",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
