from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("autenticacion_docente", "0003_alter_docente_cedula_alter_docente_correo"),
    ]

    operations = [
        # 1. Eliminar el campo 'cedula' por completo
        migrations.RemoveField(
            model_name='Docente',
            name='cedula',
        ),
        # 2. Crear nuevamente el campo 'cedula' como IntegerField y clave primaria
        migrations.AddField(
            model_name='Docente',
            name='cedula',
            field=models.IntegerField(primary_key=True, unique=True),
        ),
    ]
