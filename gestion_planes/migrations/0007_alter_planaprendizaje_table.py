# Generated by Django 5.1.6 on 2025-02-21 02:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gestion_planes", "0006_itemplanevaluacion_objetivo_asociado"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="planaprendizaje",
            table="planes_de_aprendizaje",
        ),
    ]
