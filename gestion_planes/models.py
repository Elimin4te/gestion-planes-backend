from typing import Iterable
from datetime import date

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now
from django.conf import settings

from autenticacion_docente.models import Docente

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.colors import black
from io import BytesIO


def ajustar_texto_pdf(texto: str, max_caracteres: int, max_lineas: int = 4, elipsis: bool = False) -> tuple[str]:
    """Funcion para ajustar los textos a las columnas de los formatos pdf."""
    if len(texto) > max_caracteres:
        # Puntos suspensivos si el texto es muy largo.
        if elipsis:
            texto = texto[:max_caracteres]
            texto = texto[:-3] + '...'
            return texto,

        lineas = []
        palabras = texto.split()
        linea_actual = ""

        for palabra in palabras:
            if len(linea_actual) + len(palabra) + 1 <= max_caracteres:
                if linea_actual:
                    linea_actual += " " + palabra
                else:
                    linea_actual = palabra
            else:
                lineas.append(linea_actual)
                linea_actual = palabra

        if linea_actual:
            lineas.append(linea_actual)

        if len(lineas) > max_lineas:
            for i in range(3):
                lineas[-1] = lineas[-1][:-3] + '...'

        return lineas

    else:
        return texto,


def dibujar_multi_linea(lienzo: canvas.Canvas, lineas: tuple[str], x: int, y: int, interlinea: int = 12):
    """Escribe multiples lineas en el PDF."""
    for linea in lineas:
        lienzo.drawString(x, y, linea)
        y -= interlinea


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


    def generar_pdf(self):
        """Genera un PDF con la información del plan de aprendizaje."""

        # Cargar el PDF de la plantilla
        plantilla_pdf = PdfReader(open(settings.BASE_DIR / "gestion_planes" / "pdfs" / "plan_de_clase.pdf", "rb"))
        pagina = plantilla_pdf.pages[0]

        # Crear un nuevo PDF en memoria
        buffer = BytesIO()
        lienzo = canvas.Canvas(buffer, pagesize=landscape(letter))
        lienzo.setFont("Helvetica", 11)

        # Escribir la información en las coordenadas de la plantilla
        lienzo.drawString(115, 506, self.pnf)  # Programa
        lienzo.drawString(330, 506, self.get_nucleo_display())  # Núcleo
        lienzo.drawString(550, 506, self.get_turno_display())  # Horario

        lienzo.drawString(165, 485, self.unidad_curricular.nombre)  # Unidad Curricular
        lienzo.drawString(530, 485, self.docente.nombre_completo)  # Profesor(a)

        lienzo.setFillColor(black)

        # Tabla de objetivos
        y = 410
        objetivos: tuple["ObjetivoPlanAprendizaje"] = self.objetivoplanaprendizaje_set.all()
        for i, objetivo in enumerate(objetivos, start=1):
            dibujar_multi_linea(lienzo, ajustar_texto_pdf(f"{i}. {objetivo.titulo}", 20), 50, y)
            dibujar_multi_linea(lienzo, ajustar_texto_pdf(objetivo.contenido, 24), 165, y)
            dibujar_multi_linea(lienzo, ajustar_texto_pdf(objetivo.get_estrategia_didactica_display(), 30), 300, y)
            dibujar_multi_linea(lienzo, ajustar_texto_pdf(objetivo.criterio_logro, 26), 480, y)
            dibujar_multi_linea(lienzo, ajustar_texto_pdf(str(objetivo.duracion_horas) + " horas", 22), 630, y)
            y -= 60

        # Guardar el PDF en memoria
        lienzo.save()
        buffer.seek(0)

        # Combinar la plantilla PDF con la información escrita
        nuevo_pdf_buffer = BytesIO(buffer.getvalue()) # Creamos un nuevo buffer a partir del valor del anterior.
        nuevo_pdf = PdfReader(nuevo_pdf_buffer)
        pagina.merge_page(nuevo_pdf.pages[0])

        # Crear el flujo de salida con el PDF combinado
        salida = PdfWriter()
        salida.add_page(pagina)
        flujo_salida = BytesIO()
        salida.write(flujo_salida)
        flujo_salida.seek(0)

        return flujo_salida


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
    titulo = models.CharField(max_length=32)
    contenido = models.TextField()
    criterio_logro = models.TextField()
    estrategia_didactica = models.CharField(max_length=4, choices=OPCIONES_ESTRATEGIAS_DIDACTICAS, default='CL')
    duracion_horas = models.SmallIntegerField(
        validators=[
            MinValueValidator(2, "Las horas de duración no pueden ser menores a 2."),
            MaxValueValidator(9, "Las horas de duración no pueden ser mayores a 9.")
        ]
    )
    evaluacion_asociada = models.ForeignKey(ItemPlanEvaluacion, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'objetivos_plan_de_aprendizaje'

    def __str__(self):
        return f"{self.plan_aprendizaje.codigo_grupo} - {self.titulo}"

    def clean(self) -> None:
        # Asignar fecha de modificación de plan de aprendizaje.
        self.plan_aprendizaje.fecha_modificacion = now()
        self.plan_aprendizaje.save()
        return super().clean()