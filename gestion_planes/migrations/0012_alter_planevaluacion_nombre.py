# Generated by Django 5.1.6 on 2025-03-04 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gestion_planes", "0011_alter_planevaluacion_nombre"),
    ]

    operations = [
        migrations.AlterField(
            model_name="planevaluacion",
            name="nombre",
            field=models.CharField(max_length=96),
        ),
    ]
