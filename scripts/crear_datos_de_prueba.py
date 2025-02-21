"""Utilidad para crear set de datos de prueba."""

from autenticacion_docente.models import Docente

from gestion_planes.models import (
    UnidadCurricular,
    PlanAprendizaje,
    PlanEvaluacion,
    ItemPlanEvaluacion,
    ObjetivoPlanAprendizaje
)

import random
from datetime import date, timedelta

def run():

    # Obtener o crear el docente
    docente, created = Docente.objects.get_or_create(
        cedula="V-28318187",
        defaults={"correo": "sidesrev@gmail.com", "nombre": "Ricardo", "apellido": "Marin"},
    )

    if created:
        print("Docente creado exitosamente.")
    else:
        print("Docente ya existía.")

    # Crear unidad curricular: Matematica Discreta
    unidad_curricular = UnidadCurricular.objects.create(
        codigo="MAT-1",
        trayecto=1,
        semestre=1,
        unidades_credito=4,
        nombre="Matemática I",
    )

    # Crear plan de aprendizaje
    plan_aprendizaje = PlanAprendizaje.objects.create(
        docente=docente,
        unidad_curricular=unidad_curricular,
        codigo_grupo="MAT-DIS-01",
        nucleo="FLO",
        turno="M",
        pnf="Ingeniería",  # Puedes ajustar el PNF
    )

    # Crear objetivos de plan de aprendizaje
    objetivos_data = [
        {
            "titulo": "Lógica proposicional",
            "contenido": "Introducción a la lógica proposicional y sus aplicaciones.",
            "criterio_logro": "El estudiante podrá resolver problemas de lógica proposicional.",
            "estrategia_didactica": "CL",
            "duracion_horas": 20,
        },
        {
            "titulo": "Reglas de inferencia",
            "contenido": "Reglas de inferencia y su uso en la demostración de argumentos.",
            "criterio_logro": "El estudiante podrá demostrar la validez de argumentos utilizando reglas de inferencia.",
            "estrategia_didactica": "AP",
            "duracion_horas": 25,
        },
        {
            "titulo": "Conjuntos y Relaciones",
            "contenido": "Teoría de conjuntos, relaciones y funciones.",
            "criterio_logro": "El estudiante podrá realizar operaciones con conjuntos y relaciones.",
            "estrategia_didactica": "TR",
            "duracion_horas": 15,
        },
        {
            "titulo": "Funciones y Grafos",
            "contenido": "Funciones, grafos y sus aplicaciones.",
            "criterio_logro": "El estudiante podrá resolver problemas utilizando funciones y grafos.",
            "estrategia_didactica": "EP",
            "duracion_horas": 20,
        },
        {
            "titulo": "Problemas de conteo",
            "contenido": "Técnicas de conteo y probabilidad.",
            "criterio_logro": "El estudiante podrá resolver problemas de conteo y probabilidad.",
            "estrategia_didactica": "TA",
            "duracion_horas": 10,
        },
        {
            "titulo": "Teoría de números",
            "contenido": "Conceptos básicos de la teoría de números.",
            "criterio_logro": "El estudiante podrá aplicar los conceptos básicos de la teoría de números.",
            "estrategia_didactica": "EX",
            "duracion_horas": 10,
        },
    ]

    objetivos = []
    for data in objetivos_data:
        objetivo = ObjetivoPlanAprendizaje.objects.create(
            plan_aprendizaje=plan_aprendizaje, **data
        )
        objetivos.append(objetivo)

    # Crear plan de evaluación
    plan_evaluacion = PlanEvaluacion.objects.create(
        plan_aprendizaje=plan_aprendizaje,
        nombre=f"Plan de Evaluación {plan_aprendizaje.codigo_grupo}",
    )

    # Crear items de plan de evaluación (sumando 100% en peso)
    items_data = [
        {
            "instrumento_evaluacion": "PR",
            "tipo_evaluacion": "SU",
            "habilidades_a_evaluar": "Lógica",
            "peso": 15,
            "objetivo_asociado": objetivos[0],
        },
        {
            "instrumento_evaluacion": "TA",
            "tipo_evaluacion": "FO",
            "habilidades_a_evaluar": "Inferencia",
            "peso": 15,
            "objetivo_asociado": objetivos[1],
        },
        {
            "instrumento_evaluacion": "PR",
            "tipo_evaluacion": "SU",
            "habilidades_a_evaluar": "Conjuntos",
            "peso": 20,
            "objetivo_asociado": objetivos[2],
        },
        {
            "instrumento_evaluacion": "TA",
            "tipo_evaluacion": "FO",
            "habilidades_a_evaluar": "Funciones",
            "peso": 20,
            "objetivo_asociado": objetivos[3],
        },
        {
            "instrumento_evaluacion": "EX",
            "tipo_evaluacion": "SU",
            "habilidades_a_evaluar": "Conteo",
            "peso": 15,
            "objetivo_asociado": objetivos[4],
        },
        {
            "instrumento_evaluacion": "PY",
            "tipo_evaluacion": "SU",
            "habilidades_a_evaluar": "Números",
            "peso": 15,
            "objetivo_asociado": objetivos[5],
        },
    ]

    # Fechas aleatorias de planificacion
    fecha_inicio = date(2024, 4, 1)
    fecha_fin = date(2024, 6, 30)

    for data in items_data:
        fecha_planificada = fecha_inicio + timedelta(
            days=random.randint(0, (fecha_fin - fecha_inicio).days)
        )
        ItemPlanEvaluacion.objects.create(
            plan_evaluacion=plan_evaluacion, **data, fecha_planificada=fecha_planificada
        )

    print("Datos de prueba creados exitosamente.")
