from django.db import models
from django.core.validators import EmailValidator, RegexValidator


class Docente(models.Model):
    """Modelo de Docente para el flujo de autenticación."""
    
    cedula = models.CharField(
        max_length=20, 
        primary_key=True,
        validators=[RegexValidator(
            regex=r"^[V]-\d{7,8}$",  # Expresión regular para validar el formato de la cédula venezolana
            message="Ingrese una cédula venezolana válida (Ej: V-12345678)",
            code="cedula_invalida"
        )]
    )
    correo = models.EmailField(
        max_length=254,
        validators=[EmailValidator(
            message="Ingrese un correo electrónico válido",
            code="correo_invalido"
        )]
    )
    nombre = models.CharField(max_length=64)
    apellido = models.CharField(max_length=64)

    class Meta:
        db_table = 'docentes'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
