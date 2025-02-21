# Generated by Django 5.1.6 on 2025-02-21 01:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gestion_planes", "0005_alter_itemplanevaluacion_table_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="itemplanevaluacion",
            name="objetivo_asociado",
            field=models.OneToOneField(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to="gestion_planes.objetivoplanaprendizaje",
            ),
        ),
    ]
