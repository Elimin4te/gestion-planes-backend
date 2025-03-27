from typing import Iterable, Any
from datetime import date
from math import ceil
from pathlib import Path

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now
from django.conf import settings

from rest_framework.serializers import ValidationError

from autenticacion_docente.models import Docente

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.colors import black
from io import BytesIO

from .utils import dibujar_multi_linea, ajustar_texto_pdf


class ExportablePDFMixin:
    """ Clase abstracta que sirve como base para definir como se genera un pdf en una entidad que se puede exportar. """

    @property
    def plantilla_para_pdf(self) -> Path:
        """ Ubicación de la plantilla. """
        return settings.BASE_DIR / "gestion_planes" / "pdfs" / f"{self.__class__.__name__.lower()}.pdf"

    @property
    def maximo_objetos_por_pagina(self):
        """ La cantidad máxima de objetivos que pueden haber en una página del PDF. """
        return 6

    @property
    def desviacion_y(self):
        """Define la cantidad de pixeles de desviacion Y del contenido."""
        return 12

    def escribir_encabezado(self, lienzo: canvas.Canvas):
        """Escribe la información del PNF, núcleo, docente y UC en el pdf.
        
        Se deben definir 5 propiedades en el modelo para este metodo:
        - nombre_pnf
        - nombre_nucleo
        - nombre_turno
        - nombre_uc
        - nombre_docente
        """

        # Escribir la información en las coordenadas de la plantilla
        lienzo.drawString(120, 506 + self.desviacion_y, self.nombre_pnf)  # Programa
        lienzo.drawString(342, 506 + self.desviacion_y, self.nombre_nucleo)  # Núcleo
        lienzo.drawString(548, 506 + self.desviacion_y, self.nombre_turno)  # Horario

        lienzo.drawString(185, 485 + self.desviacion_y, self.nombre_uc)  # Unidad Curricular
        lienzo.drawString(545, 485 + self.desviacion_y, self.nombre_docente)  # Profesor(a)

        # Fecha de Modificación (o Creación) del Plan
        lienzo.drawString(55, 30 + self.desviacion_y, (self.fecha_modificacion or self.fecha_creacion).strftime('%d/%m/%Y'))


    def llenar_tabla(self, lienzo: canvas.Canvas, datos: tuple[int, Any]):
        """Función sobrescribible donde se define la lógica para llenar la tabla de información."""
        ...

    def generar_pagina(self, datos: tuple[int, Any]):
        """Función donde se define la lógica para generar una página."""
        # Objeto de pagina base
        plantilla = PdfReader(self.plantilla_para_pdf).pages[0] 

        # Crear un nuevo PDF en memoria
        buffer = BytesIO()
        lienzo = canvas.Canvas(buffer, pagesize=landscape(letter))
        lienzo.setFont("Helvetica", 11)

        # Escribir la información encabezado
        self.escribir_encabezado(lienzo)

        lienzo.setFillColor(black)

        # Llenado de tabla
        self.llenar_tabla(lienzo, datos)

        # Guardar el PDF en memoria
        lienzo.save()
        buffer.seek(0)

        # Combinar la plantilla PDF con la información escrita
        nuevo_pdf_buffer = BytesIO(buffer.getvalue()) # Creamos un nuevo buffer a partir del valor del anterior.
        nuevo_pdf = PdfReader(nuevo_pdf_buffer)
        plantilla.merge_page(nuevo_pdf.pages[0])

        return plantilla

    def validar_datos_para_exportar(self, items: tuple = None):
        """Valida que los datos a exportar sean aceptables."""
        ...

    def generar_pdf(self):
        """Genera las páginas del archivo y devuelve el buffer de bytes final."""

        # Crear el flujo de salida con el PDF combinado
        salida = PdfWriter()
        items = self.obtener_items_pdf()
        self.validar_datos_para_exportar(items)

        # Enumera y separa los items
        items = enumerate(items, 1)
        items = tuple((idx, item) for idx, item in items)

        # Se dividen los objetivos según la cantidad máxima de entradas por PDF
        paginas_requeridas = ceil(len(items) / self.maximo_objetos_por_pagina)
        partes = tuple(
            [
                items[
                    self.maximo_objetos_por_pagina*i:self.maximo_objetos_por_pagina*(i+1)
                ] for i in range(0, paginas_requeridas)
            ]
        )

        # Se generan las paginas para cada parte y se agregan a la salida
        for parte in partes:
            salida.add_page(self.generar_pagina(parte))

        flujo_salida = BytesIO()
        salida.write(flujo_salida)
        flujo_salida.seek(0)

        return flujo_salida

    def obtener_items_pdf(self) -> tuple[Any]:
        """Función sobrescribible donde se debe declarar el set de datos origen para el pdf."""
        ...


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
        return f"{self.nombre} ({self.codigo})"


OPCIONES_NUCLEO = [
    ('FLO', 'La Floresta'),
    ('URB', 'La Urbina'),
    ('ALT', 'Altagracia'),
    ('LGA', 'La Guaira')
]

OPCIONES_TURNO = [
    ('N', 'Nocturno'),
    ('V', 'Vespertino'),
    ('M', 'Matutino'),
    ('S', 'Sabatino'),
]


class PlanAprendizaje(models.Model, ExportablePDFMixin):
    """Modelo de plan de aprendizaje."""

    codigo_grupo = models.CharField(max_length=32, primary_key=True)
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    unidad_curricular = models.ForeignKey(UnidadCurricular, on_delete=models.CASCADE)
    nucleo = models.CharField(max_length=6, choices=OPCIONES_NUCLEO)
    turno = models.CharField(max_length=3, choices=OPCIONES_TURNO)
    pnf = models.CharField(max_length=32)
    fecha_creacion = models.DateTimeField(default=now)
    fecha_modificacion = models.DateTimeField(null=True)

    @property
    def nombre_pnf(self) -> str:
        return self.pnf

    @property
    def nombre_nucleo(self) -> str:
        return self.get_nucleo_display()

    @property
    def nombre_turno(self) -> str:
        return self.get_turno_display()

    @property
    def nombre_uc(self) -> str:
        return self.unidad_curricular.nombre

    @property
    def nombre_docente(self) -> str:
        return self.docente.nombre_completo

    class Meta:
        db_table = 'planes_de_aprendizaje'

    def __str__(self):
        return f"P.A {self.unidad_curricular.nombre} por {self.docente.nombre_completo} ({self.codigo_grupo})"

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

    def llenar_tabla(self, lienzo: canvas.Canvas, datos: tuple[int, "ObjetivoPlanAprendizaje"]):
        """ Escribe los objetivos de aprendizaje en la tabla de la plantilla. """
        y = 412
        for i, objetivo in datos:
            objetivo: ObjetivoPlanAprendizaje
            dibujar_multi_linea(lienzo, ajustar_texto_pdf(f"{i}. {objetivo.titulo}", 30), 37, y)
            dibujar_multi_linea(lienzo, ajustar_texto_pdf(objetivo.contenido, 40), 190, y)
            dibujar_multi_linea(lienzo, ajustar_texto_pdf(objetivo.get_estrategia_didactica_display(), 18), 390, y)
            dibujar_multi_linea(lienzo, ajustar_texto_pdf(objetivo.criterio_logro, 30), 508, y)
            dibujar_multi_linea(lienzo, ajustar_texto_pdf(str(objetivo.duracion_horas) + " horas", 16), 690, y)
            y -= 58

    def obtener_items_pdf(self) -> tuple["ObjetivoPlanAprendizaje"]:
        return self.objetivoplanaprendizaje_set.all()

    
    def validar_datos_para_exportar(self, items: tuple["ObjetivoPlanAprendizaje"]):

        items_sin_evaluacion: tuple["ObjetivoPlanAprendizaje"] = tuple(filter(lambda item: item.evaluacion_asociada is None, items))
        items_sin_evaluacion = [item.titulo for item in items_sin_evaluacion]
        if len(items_sin_evaluacion) > 0:
            raise ValidationError(
                f"No se puede exportar el plan ya que hay objetivos de plan de aprendizaje sin evaluación asociada: {', '.join(items_sin_evaluacion)}"
            )


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

class PlanEvaluacion(models.Model, ExportablePDFMixin):
    """Modelo de plan de evaluación."""

    nombre = models.CharField(max_length=96)
    fecha_creacion = models.DateTimeField(default=now)
    fecha_modificacion = models.DateTimeField(null=True)

    # Relación 1:1 con Plan de Aprendizaje
    plan_aprendizaje = models.OneToOneField(PlanAprendizaje, on_delete=models.CASCADE)

    @property
    def nombre_pnf(self) -> str:
        return self.plan_aprendizaje.nombre_pnf

    @property
    def nombre_nucleo(self) -> str:
        return self.plan_aprendizaje.nombre_nucleo

    @property
    def nombre_turno(self) -> str:
        return self.plan_aprendizaje.nombre_turno

    @property
    def nombre_uc(self) -> str:
        return self.plan_aprendizaje.nombre_uc

    @property
    def nombre_docente(self) -> str:
        return self.plan_aprendizaje.nombre_docente

    class Meta:
        db_table = 'planes_de_evaluacion'

    def __str__(self):
        return f"P.E {self.nombre} ({self.plan_aprendizaje.codigo_grupo})"

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
        objetivo_asociado: "ObjetivoPlanAprendizaje",
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

    def llenar_tabla(self, lienzo: canvas.Canvas, datos: tuple[int, "ItemPlanEvaluacion"]):
        """ Escribe los items del plan de evaluación en la tabla de la plantilla. """
        y = 412
        for i, evaluacion in datos:
            evaluacion: ItemPlanEvaluacion
            objetivos = ", ".join(obj.titulo for obj in evaluacion.objetivos)
            dibujar_multi_linea(lienzo, ajustar_texto_pdf(evaluacion.get_instrumento_evaluacion_display(), 24), 37, y)
            dibujar_multi_linea(lienzo, ajustar_texto_pdf(evaluacion.get_tipo_evaluacion_display(), 24), 195, y)
            dibujar_multi_linea(lienzo, ajustar_texto_pdf(f"{objetivos}", 36), 313, y)
            dibujar_multi_linea(lienzo, ajustar_texto_pdf(evaluacion.habilidades_a_evaluar, 39), 483, y)
            dibujar_multi_linea(lienzo, ajustar_texto_pdf(str(evaluacion.peso) + "%", 22), 714, y)
            y -= 58

    def obtener_items_pdf(self) -> tuple["ItemPlanEvaluacion"]:
        return self.itemplanevaluacion_set.all()


    def validar_datos_para_exportar(self, items: tuple["ItemPlanEvaluacion"]):

        self.plan_aprendizaje.validar_datos_para_exportar()
        peso_total = sum(item.peso for item in items) 
        if not peso_total == 100:
            raise ValidationError(f"El plan de evaluacion debe tener un total de 100%, actualmente tiene {peso_total}%.")



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
    fecha_planificada = models.DateField()

    @property
    def objetivos(self) -> tuple["ObjetivoPlanAprendizaje"]:
        return self.objetivos_asociados.all()

    class Meta:
        db_table = 'items_plan_de_evaluacion'

    def __str__(self):
        return f"{self.tipo_evaluacion}-{self.instrumento_evaluacion} {self.peso}% ({self.plan_evaluacion.nombre})"

    def clean(self):
        super().clean()
        self.validar_suma_pesos()

        # Asignar fecha de modificación de plan de evaluación.
        self.plan_evaluacion.fecha_modificacion = now()
        self.plan_evaluacion.save()


    def agregar_objetivo(
        self,
        objetivo: "ObjetivoPlanAprendizaje",
    ):

        """ Agrega un objetivo (existente o no) a esta evaluación. """

        objetivo.evaluacion_asociada = self
        objetivo.save()
        return objetivo

    def validar_suma_pesos(self):
        """Valida que la suma de los pesos de los ítems no exceda el 100%."""

        # Obtiene todos los ítems del plan de evaluación
        items: Iterable[ItemPlanEvaluacion] = ItemPlanEvaluacion.objects.filter(plan_evaluacion=self.plan_evaluacion)
        suma_pesos = sum(item.peso for item in items)

        if suma_pesos > 100:
            raise ValidationError(
                "La suma de los pesos de los ítems no puede exceder el 100%."
            )


class ObjetivoPlanAprendizaje(models.Model):
    """Modelo de objetivos de plan de aprendizaje."""

    plan_aprendizaje = models.ForeignKey(PlanAprendizaje, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=64)
    contenido = models.TextField()
    criterio_logro = models.TextField()
    estrategia_didactica = models.CharField(max_length=4, choices=OPCIONES_ESTRATEGIAS_DIDACTICAS, default='CL')
    duracion_horas = models.SmallIntegerField(
        validators=[
            MinValueValidator(2, "Las horas de duración no pueden ser menores a 2."),
            MaxValueValidator(9, "Las horas de duración no pueden ser mayores a 9.")
        ]
    )
    evaluacion_asociada = models.ForeignKey(
        ItemPlanEvaluacion, on_delete=models.SET_NULL, null=True, related_name="objetivos_asociados"
    )

    class Meta:
        db_table = 'objetivos_plan_de_aprendizaje'

    def __str__(self):
        return f"{self.plan_aprendizaje.codigo_grupo} - {self.titulo}"

    def clean(self) -> None:
        # Asignar fecha de modificación de plan de aprendizaje.
        self.plan_aprendizaje.fecha_modificacion = now()
        self.plan_aprendizaje.save()
        return super().clean()