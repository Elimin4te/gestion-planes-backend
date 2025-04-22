from django.db import models
from django.core.validators import EmailValidator, MinValueValidator, MaxValueValidator

# Funcion de atajo para formatear la cedula usando punto como separador de miles en vez de coma.
def _(numero: int):
    return f"{numero:,}".replace(",", ".")

NUMERO_MINIMO_CEDULA = 1_000_000
NUMERO_MAXIMO_CEDULA = 35_000_000

MENSAJE_CEDULA_INVALIDA = (
    f"Ingrese un número de cédula válido (Entre {_(NUMERO_MINIMO_CEDULA)} y {_(NUMERO_MAXIMO_CEDULA)})"
)

class Docente(models.Model):
    """Modelo de Docente para el flujo de autenticación."""
    
    cedula = models.IntegerField(
        max_length=20, 
        primary_key=True,
        validators=[
            MinValueValidator(NUMERO_MINIMO_CEDULA, MENSAJE_CEDULA_INVALIDA),
            MaxValueValidator(NUMERO_MAXIMO_CEDULA, MENSAJE_CEDULA_INVALIDA)
        ]
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
        constraints = [
            models.CheckConstraint(
                check=models.Q(cedula__gte=NUMERO_MINIMO_CEDULA),
                name='cedula_mayor_que',
                violation_error_message=MENSAJE_CEDULA_INVALIDA
            ),
            models.CheckConstraint(
                check=models.Q(cedula__lte=NUMERO_MAXIMO_CEDULA),
                name='cedula_menor_que',
                violation_error_message=MENSAJE_CEDULA_INVALIDA
            )
        ]

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({_(self.cedula)})"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
