""" Utilidad para limpiar la base de datos. """

from autenticacion_docente.models import Docente

from gestion_planes.models import (
    UnidadCurricular,
    PlanAprendizaje,
    PlanEvaluacion,
    ItemPlanEvaluacion,
    ObjetivoPlanAprendizaje
)

def run():
    # Eliminar todos los datos de las tablas
    ItemPlanEvaluacion.objects.all().delete()
    PlanEvaluacion.objects.all().delete()
    ObjetivoPlanAprendizaje.objects.all().delete()
    PlanAprendizaje.objects.all().delete()
    UnidadCurricular.objects.all().delete()
    Docente.objects.all().delete()

    print("Datos de la base de datos eliminados exitosamente.")