"""Utilidad para crear set de datos de prueba."""

from autenticacion_docente.models import Docente

from django.db.models import Model

from gestion_planes.models import (
    UnidadCurricular,
    PlanAprendizaje,
    PlanEvaluacion,
    ItemPlanEvaluacion,
    ObjetivoPlanAprendizaje,
    OPCIONES_TURNO,
    OPCIONES_NUCLEO,
    OPCIONES_ESTRATEGIAS_DIDACTICAS,
    OPCIONES_INSTRUMENTOS_EVALUACION,
    OPCIONES_TIPO_EVALUACION,
)

import random
from datetime import date, datetime, timedelta


def crear_si_no_existe(entidad: Model, campo_pk, valor_pk: str, datos: dict):

    objeto, creado = entidad.objects.get_or_create(
        **{campo_pk: valor_pk},
        defaults=datos,
    )

    if creado:
        print(f"{entidad.__name__} {valor_pk} creado(a) exitosamente.")
    else:
        print(f"{entidad.__name__} {valor_pk} ya existía.")

    return objeto


def opcion_aleatoria(opciones: list[tuple[str, str]]) -> str:
    return random.choice(opciones)[0]


def crear_docentes():

    return (
        crear_si_no_existe(
            entidad=Docente,
            campo_pk="cedula",
            valor_pk="V-28318187",
            datos={
                "correo": "sidesrev@gmail.com",
                "nombre": "Ricardo",
                "apellido": "Marin",
            },
        ),
        crear_si_no_existe(
            entidad=Docente,
            campo_pk="cedula",
            valor_pk="V-22807503",
            datos={
                "correo": "vhoggin0@free.fr",
                "nombre": "Victoria",
                "apellido": "Hoggin",
            },
        ),
        crear_si_no_existe(
            entidad=Docente,
            campo_pk="cedula",
            valor_pk="V-26333054",
            datos={
                "correo": "jperez1@eepurl.com",
                "nombre": "José",
                "apellido": "Pérez",
            },
        ),
    )


def crear_unidades_curriculares():

    return (
        crear_si_no_existe(
            entidad=UnidadCurricular,
            campo_pk="codigo",
            valor_pk="MAT-1",
            datos={
                "trayecto": 1,
                "semestre": 1,
                "unidades_credito": 4,
                "nombre": "Matemática I",
            },
        ),
        crear_si_no_existe(
            entidad=UnidadCurricular,
            campo_pk="codigo",
            valor_pk="FC-1",
            datos={
                "trayecto": 1,
                "semestre": 2,
                "unidades_credito": 2,
                "nombre": "Formación Crítica I",
            },
        ),
        crear_si_no_existe(
            entidad=UnidadCurricular,
            campo_pk="codigo",
            valor_pk="AYP-0",
            datos={
                "trayecto": 2,
                "semestre": 1,
                "unidades_credito": 3,
                "nombre": "Algorítmica y Programación",
            },
        ),
    )


def crear_plan_aprendizaje(docente: Docente, uc: UnidadCurricular, pnf: str):

    nucleo = opcion_aleatoria(OPCIONES_NUCLEO)
    turno = opcion_aleatoria(OPCIONES_TURNO)

    año = datetime.now().year
    codigo_grupo = f"INF-({uc.codigo})-{nucleo}-{turno} ({año}-{año + 1})"

    return crear_si_no_existe(
        entidad=PlanAprendizaje,
        campo_pk="codigo_grupo",
        valor_pk=codigo_grupo,
        datos={
            "unidad_curricular": uc,
            "docente": docente,
            "nucleo": nucleo,
            "turno": turno,
            "pnf": pnf,
        },
    )


def crear_objetivo_pa(
    pa: PlanAprendizaje, titulo: str, contenido: str, criterio_logro: str
):

    estrategia_didactica = opcion_aleatoria(OPCIONES_ESTRATEGIAS_DIDACTICAS)
    duracion_horas = random.randint(2, 9)

    return crear_si_no_existe(
        ObjetivoPlanAprendizaje,
        campo_pk="titulo",
        valor_pk=titulo,
        datos={
            "plan_aprendizaje": pa,
            "estrategia_didactica": estrategia_didactica,
            "duracion_horas": duracion_horas,
            "contenido": contenido,
            "criterio_logro": criterio_logro,
        },
    )


def crear_plan_evaluacion(pa: PlanAprendizaje):

    nombre = f"P.E de {pa.nombre_uc} ({pa.codigo_grupo})"

    return crear_si_no_existe(
        PlanEvaluacion,
        campo_pk="plan_aprendizaje",
        valor_pk=pa,
        datos={"nombre": nombre},
    )


def crear_item_pe(
    pe: PlanEvaluacion, 
    habilidades_a_evaluar: str, 
    peso: int, 
    objetivos_asociados: tuple[ObjetivoPlanAprendizaje] = ()
):

    instrumento_evaluacion = opcion_aleatoria(OPCIONES_INSTRUMENTOS_EVALUACION)
    tipo_evaluacion = opcion_aleatoria(OPCIONES_TIPO_EVALUACION)

    fecha_inicio = date(2025, 4, 1)
    fecha_fin = date(2025, 10, 30)
    fecha_planificada = fecha_inicio + timedelta(
        days=random.randint(0, (fecha_fin - fecha_inicio).days)
    )

    item_pe = crear_si_no_existe(
        ItemPlanEvaluacion,
        campo_pk="habilidades_a_evaluar",
        valor_pk=habilidades_a_evaluar,
        datos={
            "plan_evaluacion": pe,
            "peso": peso,
            "fecha_planificada": fecha_planificada,
            "instrumento_evaluacion": instrumento_evaluacion,
            "tipo_evaluacion": tipo_evaluacion,
        },
    )

    for obj in objetivos_asociados:
        item_pe.agregar_objetivo(obj)

    return item_pe


def run():

    rmarin, vhoggin, jperez = crear_docentes()
    mat1, fc1, ayp = crear_unidades_curriculares()

    pnf = "Informática (PNFi)"

    pa_mat1 = crear_plan_aprendizaje(rmarin, mat1, pnf)
    pa_fc1 = crear_plan_aprendizaje(vhoggin, fc1, pnf)
    pa_ayp = crear_plan_aprendizaje(jperez, ayp, pnf)

    data_objetivos_mat1 = [
        {
            "titulo": "Conceptos básicos del álgebra",
            "contenido": "Definir y aplicar los conceptos de variables, expresiones algebraicas, ecuaciones y desigualdades.",
            "criterio_logro": "Resolver correctamente ecuaciones y desigualdades lineales y cuadráticas.",
        },
        {
            "titulo": "Operaciones con funciones",
            "contenido": "Realizar operaciones de suma, resta, multiplicación, división y composición de funciones.",
            "criterio_logro": "Calcular y simplificar correctamente las operaciones con funciones dadas.",
        },
        {
            "titulo": "Límite de una función",
            "contenido": "Calcular límites de funciones algebraicas y trascendentes, utilizando diferentes técnicas.",
            "criterio_logro": "Determinar la existencia y el valor de límites de funciones en puntos y en el infinito.",
        },
        {
            "titulo": "Derivadas de funciones",
            "contenido": "Aplicar las reglas de derivación para calcular derivadas de funciones algebraicas, trigonométricas, exponenciales y logarítmicas.",
            "criterio_logro": "Calcular derivadas de funciones utilizando la regla de la cadena, la regla del producto y la regla del cociente.",
        },
        {
            "titulo": "Integral definida",
            "contenido": "Calcular integrales definidas utilizando el teorema fundamental del cálculo.",
            "criterio_logro": "Aplicar la integral definida para calcular áreas bajo curvas y volúmenes de sólidos de revolución.",
        },
        {
            "titulo": "Integrales definidas: problemas",
            "contenido": "Resolver problemas de integrales definidas utilizando el teorema fundamental del cálculo.",
            "criterio_logro": "Aplicar la integral definida para calcular áreas bajo curvas y volúmenes de sólidos de revolución.",
        },
        {
            "titulo": "Aplicación de cálculo",
            "contenido": "Aplicar los conceptos de límites, derivadas e integrales para resolver problemas de optimización, tasas de cambio y acumulación.",
            "criterio_logro": "Plantear y resolver problemas de aplicación de cálculo en diferentes contextos.",
        },
    ]

    objetivos_mat1 = [
        crear_objetivo_pa(pa_mat1, o["titulo"], o["contenido"], o["criterio_logro"])
        for o in data_objetivos_mat1
    ]

    data_objetivos_fc1 = [
        {
            "titulo": "Argumentos",
            "contenido": "Distinguir entre opiniones y argumentos, reconocer la estructura de un argumento y evaluar su validez.",
            "criterio_logro": "Analizar textos y discursos identificando la presencia de argumentos y evaluando su solidez.",
        },
        {
            "titulo": "Credibilidad de las fuentes",
            "contenido": "Aplicar criterios para evaluar la confiabilidad y relevancia de las fuentes de información.",
            "criterio_logro": "Seleccionar fuentes de información confiables para la investigación y el análisis.",
        },
        {
            "titulo": "Sesgos cognitivos",
            "contenido": "Identificar los principales sesgos cognitivos y comprender su influencia en el pensamiento y la toma de decisiones.",
            "criterio_logro": "Aplicar estrategias para mitigar el impacto de los sesgos cognitivos en el análisis de información y la resolución de problemas.",
        },
        {
            "titulo": "Problemas sociales",
            "contenido": "Analizar problemas sociales desde una perspectiva crítica, considerando diferentes puntos de vista y evidencias.",
            "criterio_logro": "Desarrollar soluciones creativas e informadas a problemas sociales, utilizando el pensamiento crítico como herramienta fundamental.",
        },
    ]

    objetivos_fc1 = [
        crear_objetivo_pa(pa_fc1, o["titulo"], o["contenido"], o["criterio_logro"])
        for o in data_objetivos_fc1
    ]

    data_objetivos_ayp = [
        {
            "titulo": "Fundamentos de la algorítmica",
            "contenido": "Definir y aplicar conceptos como algoritmos, variables, estructuras de control y tipos de datos.",
            "criterio_logro": "Diseñar algoritmos para resolver problemas sencillos, utilizando diagramas de flujo y pseudocódigo.",
        },
        {
            "titulo": "Estructuras de control",
            "contenido": "Utilizar estructuras de control secuenciales, condicionales (if, else) y repetitivas (for, while) para controlar el flujo de un programa.",
            "criterio_logro": "Implementar programas que utilicen estructuras de control para resolver problemas más complejos.",
        },
        {
            "titulo": "Funciones",
            "contenido": "Definir y utilizar funciones para modularizar el código y reutilizar funcionalidades.",
            "criterio_logro": "Desarrollar programas que utilicen funciones para dividir problemas complejos en tareas más pequeñas.",
        },
        {
            "titulo": "Arreglos y listas",
            "contenido": "Utilizar arreglos y listas para almacenar y manipular colecciones de datos.",
            "criterio_logro": "Implementar programas que utilicen arreglos y listas para resolver problemas de búsqueda, ordenamiento y manipulación de datos.",
        },
        {
            "titulo": "Algoritmos de búsqueda y ordenamiento",
            "contenido": "Comprender e implementar algoritmos de búsqueda lineal y binaria, así como algoritmos de ordenamiento como burbuja, selección e inserción.",
            "criterio_logro": "Comparar la eficiencia de diferentes algoritmos de búsqueda y ordenamiento para resolver problemas específicos.",
        },
    ]

    objetivos_ayp = [
        crear_objetivo_pa(pa_ayp, o["titulo"], o["contenido"], o["criterio_logro"])
        for o in data_objetivos_ayp
    ]

    pe_mat1 = crear_plan_evaluacion(pa_mat1)
    pe_fc1 = crear_plan_evaluacion(pa_fc1)
    pe_ayp = crear_plan_evaluacion(pa_ayp)

    data_items_mat1 = [
        {
            "habilidades_a_evaluar": "Resolución de ecuaciones y desigualdades algebraicas",
            "peso": 20,
            "objetivos_asociados": (objetivos_mat1[0],)
        },
        {
            "habilidades_a_evaluar": "Operaciones con funciones (suma, resta, multiplicación, división, composición)",
            "peso": 20,
            "objetivos_asociados": (objetivos_mat1[1],)
        },
        {
            "habilidades_a_evaluar": "Cálculo de límites de funciones", 
            "peso": 15,
            "objetivos_asociados": (objetivos_mat1[2],)
        },
        {
            "habilidades_a_evaluar": "Cálculo de derivadas de funciones (reglas básicas y derivadas de orden superior)",
            "peso": 20,
            "objetivos_asociados": (objetivos_mat1[3],)
        },
        {
            "habilidades_a_evaluar": "Cálculo de integrales definidas", 
            "peso": 25,
            "objetivos_asociados": objetivos_mat1[4:6]
        },
    ]

    items_mat1 = [
        crear_item_pe(pe_mat1, o["habilidades_a_evaluar"], o["peso"], o["objetivos_asociados"])
        for o in data_items_mat1
    ]

    data_items_fc1 = [
        {
            "habilidades_a_evaluar": "Análisis y evaluación de argumentos en textos y discursos",
            "peso": 25,
            "objetivos_asociados": (objetivos_fc1[0],)
        },
        {
            "habilidades_a_evaluar": "Evaluación de la credibilidad y relevancia de fuentes de información",
            "peso": 25,
            "objetivos_asociados": (objetivos_fc1[1],)
        },
        {
            "habilidades_a_evaluar": "Identificación y análisis de sesgos cognitivos en situaciones reales",
            "peso": 25,
            "objetivos_asociados": (objetivos_fc1[2],)
        },
        {
            "habilidades_a_evaluar": "Aplicación del pensamiento crítico en la resolución de problemas sociales",
            "peso": 25,
            "objetivos_asociados": (objetivos_fc1[3],)
        },
    ]

    items_fc1 = [
        crear_item_pe(pe_fc1, o["habilidades_a_evaluar"], o["peso"], o["objetivos_asociados"])
        for o in data_items_fc1
    ]

    data_items_ayp = [
        {
            "habilidades_a_evaluar": "Diseño de algoritmos en pseudocódigo y diagramas de flujo",
            "peso": 15,
            "objetivos_asociados": (objetivos_ayp[0],)
        },
        {
            "habilidades_a_evaluar": "Implementación de programas con estructuras de control (if, else, for, while)",
            "peso": 20,
            "objetivos_asociados": (objetivos_ayp[1],)
        },
        {
            "habilidades_a_evaluar": "Desarrollo de programas utilizando funciones y modularización",
            "peso": 20,
            "objetivos_asociados": (objetivos_ayp[2],)
        },
        {
            "habilidades_a_evaluar": "Manejo y manipulación de arreglos y listas en programas",
            "peso": 20,
            "objetivos_asociados": (objetivos_ayp[3],)
        },
        {
            "habilidades_a_evaluar": "Resolución de problemas prácticos aplicando los conceptos de programación",
            "peso": 25,
            "objetivos_asociados": (objetivos_ayp[4],)
        },
    ]

    items_ayp = [
        crear_item_pe(pe_ayp, o["habilidades_a_evaluar"], o["peso"], o["objetivos_asociados"])
        for o in data_items_ayp
    ]

    print("Datos de prueba creados exitosamente.")
