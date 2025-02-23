# Generated by Django 5.1.6 on 2025-02-21 01:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("autenticacion_docente", "0002_alter_docente_table"),
    ]

    operations = [
        migrations.AlterField(
            model_name="docente",
            name="cedula",
            field=models.CharField(
                max_length=20,
                primary_key=True,
                serialize=False,
                validators=[
                    django.core.validators.RegexValidator(
                        code="cedula_invalida",
                        message="Ingrese una cédula venezolana válida (Ej: V-12345678)",
                        regex="^[V]-\\d{7,8}$",
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="docente",
            name="correo",
            field=models.EmailField(
                max_length=254,
                validators=[
                    django.core.validators.EmailValidator(
                        code="correo_invalido",
                        message="Ingrese un correo electrónico válido",
                    )
                ],
            ),
        ),
    ]
