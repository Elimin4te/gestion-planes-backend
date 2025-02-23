from typing import Iterable, Optional
from datetime import date

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now

from autenticacion_docente.models import Docente


OPCIONES_TRAYECTO = [
    (0, 'Inicial'),
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
]

OPCIONES_SEMESTRE = [
    ('NA', 'No Aplica'),
    (1, '1'),
    (2, '2'),
]

class UnidadCurricular(models.Model):
    """Modelo de unidad curricular."""

    codigo = models.CharField(max_length=20, primary_key=True)
    trayecto = models.SmallIntegerField(choices=OPCIONES_TRAYECTO)
    semestre = models.SmallIntegerField(choices=OPCIONES_SEMESTRE)
    unidades_credito = models.SmallIntegerField(
        validators=[
            MinValueValidator(1, "Las unidades de crédito no pueden ser menores a 1."),
            MaxValueValidator(10, "Las unidades de crédito no pueden ser mayores a 10.")
        ]
    )
    nombre = models.CharField(max_length=32)

    class Meta:
        db_table = 'unidades_curriculares'

    def __str__(self):
        return self.nombre


OPCIONES_NUCLEO = [
    ('FLO', 'La Floresta'),
    ('URB', 'La Urbina'),
    ('ALT', 'Altagracia'),
    ('CRY', 'Carayaca')
]

OPCIONES_TURNO = [
    ('N', 'Nocturno'),
    ('V', 'Vespertino'),
    ('M', 'Mañana')
]


class PlanAprendizaje(models.Model):
    """Modelo de plan de aprendizaje."""

    codigo_grupo = models.CharField(max_length=24, primary_key=True)
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    unidad_curricular = models.ForeignKey(UnidadCurricular, on_delete=models.CASCADE)
    nucleo = models.CharField(max_length=6, choices=OPCIONES_NUCLEO)
    turno = models.CharField(max_length=3, choices=OPCIONES_TURNO)
    pnf = models.CharField(max_length=32)
    fecha_creacion = models.DateTimeField(default=now)
    fecha_modificacion = models.DateTimeField(null=True)

    class Meta:
        db_table = 'planes_de_aprendizaje'

    def __str__(self):
        return f"Plan de {self.unidad_curricular.nombre} ({self.docente.nombre})"

    def save(self, *args, **kwargs) -> None:
        # Actualiza fecha de modificación
        self.fecha_modificacion = now()
        return super().save(*args, **kwargs)

    def añadir_objetivo(
        self,
        titulo: str,
        contenido: str,
        criterio_logro: str,
        estrategia_didactica: str,
        duracion_horas: int
    ) -> "ObjetivoPlanAprendizaje":
        """Añade un nuevo objetivo al plan de aprendizaje."""

        objetivo = ObjetivoPlanAprendizaje.objects.create(
            plan_aprendizaje=self,
            titulo=titulo,
            contenido=contenido,
            criterio_logro=criterio_logro,
            estrategia_didactica=estrategia_didactica,
            duracion_horas=duracion_horas
        )

        return objetivo


OPCIONES_ESTRATEGIAS_DIDACTICAS = [
    ('CL', 'Clase magistral'),
    ('TR', 'Trabajo en grupo'),
    ('DE', 'Debate'),
    ('EP', 'Estudio de caso'),
    ('AP', 'Aprendizaje basado en problemas'),
    ('PY', 'Proyecto'),
    ('TA', 'Taller'),
    ('LB', 'Laboratorio'),
    ('EX', 'Exposición'),
    ('SE', 'Seminario'),
    ('TI', 'Tutoría individual'),
    ('TC', 'Tutoría colectiva'),
    ('VA', 'Visita guiada'),
    ('PC', 'Práctica de campo'),
    ('EV', 'Evaluación'),
    ('OT', 'Otras'),
]

class ObjetivoPlanAprendizaje(models.Model):
    """Modelo de objetivos de plan de aprendizaje."""

    plan_aprendizaje = models.ForeignKey(PlanAprendizaje, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=32)
    contenido = models.TextField()
    criterio_logro = models.TextField()
    estrategia_didactica = models.CharField(max_length=4, choices=OPCIONES_ESTRATEGIAS_DIDACTICAS, default='CL')
    duracion_horas = models.SmallIntegerField(
        validators=[
            MinValueValidator(10, "Las horas de duración no pueden ser menores a 10."),
            MaxValueValidator(200, "Las horas de duración no pueden ser mayores a 200.")
        ]
    )

    class Meta:
        db_table = 'objetivos_plan_de_aprendizaje'

    def __str__(self):
        return self.titulo

    def clean(self) -> None:
        # Asignar fecha de modificación de plan de aprendizaje.
        self.plan_aprendizaje.fecha_modificacion = now()
        self.plan_aprendizaje.save()
        return super().clean()


class PlanEvaluacion(models.Model):
    """Modelo de plan de evaluación."""

    nombre = models.CharField(max_length=32)
    fecha_creacion = models.DateTimeField(default=now)
    fecha_modificacion = models.DateTimeField(null=True)

    # Relación 1:1 con Plan de Aprendizaje
    plan_aprendizaje = models.OneToOneField(PlanAprendizaje, on_delete=models.CASCADE)

    class Meta:
        db_table = 'planes_de_evaluacion'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs) -> None:
        # Actualiza fecha de modificación
        self.fecha_modificacion = now()
        return super().save(*args, **kwargs)

    def añadir_item_evaluacion(
        self,
        instrumento_evaluacion: str,
        tipo_evaluacion: str,
        habilidades_a_evaluar: str,
        peso: int,
        objetivo_asociado: ObjetivoPlanAprendizaje,
        fecha_planificada: date
    ) -> "ItemPlanEvaluacion":
        """Añade un nuevo ítem al plan de evaluación."""

        item = ItemPlanEvaluacion.objects.create(
            plan_evaluacion=self,
            instrumento_evaluacion=instrumento_evaluacion,
            tipo_evaluacion=tipo_evaluacion,
            habilidades_a_evaluar=habilidades_a_evaluar,
            peso=peso,
            objetivo_asociado=objetivo_asociado,
            fecha_planificada=fecha_planificada
        )

        return item


OPCIONES_INSTRUMENTOS_EVALUACION = [
    ('PR', 'Prueba escrita (objetiva)'),
    ('PE', 'Prueba escrita (ensayo)'),
    ('PO', 'Prueba oral'),
    ('TR', 'Trabajo escrito'),
    ('TA', 'Tarea'),
    ('EX', 'Examen práctico'),
    ('PY', 'Proyecto'),
    ('IN', 'Informe'),
    ('PC', 'Participación en clase'),
    ('AC', 'Actividades colaborativas'),
    ('DE', 'Debate'),
    ('EX', 'Exposición oral'),
    ('SE', 'Seminario'),
    ('CT', 'Control de lectura'),
    ('CV', 'Cuestionario'),
    ('DI', 'Diario reflexivo'),
    ('CA', 'Carpeta de trabajos'),
    ('AU', 'Autoevaluación'),
    ('CO', 'Coevaluación'),
    ('OT', 'Otras'),
]

OPCIONES_TIPO_EVALUACION = [
    ('DI', 'Diagnóstica'),
    ('FO', 'Formativa'),
    ('SU', 'Sumativa'),
    ('AU', 'Autoevaluación'),
    ('CO', 'Coevaluación'),
]

OPCIONES_PESO_EVALUACION = [
    (5, '5%'),
    (10, '10%'),
    (15, '15%'),
    (20, '20%'),
    (25, '25%'),
]


class ItemPlanEvaluacion(models.Model):
    """Modelo de items de plan de evaluación."""

    plan_evaluacion = models.ForeignKey(PlanEvaluacion, on_delete=models.CASCADE)
    instrumento_evaluacion = models.CharField(max_length=4, choices=OPCIONES_INSTRUMENTOS_EVALUACION, default='PR')
    tipo_evaluacion = models.CharField(max_length=4, choices=OPCIONES_TIPO_EVALUACION, default='FO')
    habilidades_a_evaluar = models.TextField()
    peso = models.SmallIntegerField(choices=OPCIONES_PESO_EVALUACION, default=15)
    objetivo_asociado = models.OneToOneField(ObjetivoPlanAprendizaje, on_delete=models.CASCADE, default=None)
    fecha_planificada = models.DateField()

    class Meta:
        db_table = 'items_plan_de_evaluacion'

    def __str__(self):
        return f"Item de {self.plan_evaluacion.nombre}"

    def clean(self):
        super().clean()
        self.validar_suma_pesos()

        # Asignar fecha de modificación de plan de evaluación.
        self.plan_evaluacion.fecha_modificacion = now()
        self.plan_evaluacion.save()

    def validar_suma_pesos(self):
        """Valida que la suma de los pesos de los ítems no exceda el 100%."""

        # Obtiene todos los ítems del plan de evaluación
        items: Iterable[ItemPlanEvaluacion] = ObjetivoPlanAprendizaje.objects.filter(plan_evaluacion=self.plan_evaluacion)
        suma_pesos = sum(item.peso for item in items)

        if suma_pesos > 100:
            raise ValidationError(
                "La suma de los pesos de los ítems no puede exceder el 100%."
            )
