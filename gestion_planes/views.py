from rest_framework import generics
from .models import (
    UnidadCurricular,
    PlanAprendizaje,
    ObjetivoPlanAprendizaje,
    PlanEvaluacion,
    ItemPlanEvaluacion,
)
from .serializers import (
    SerializadorUnidadCurricular,
    SerializadorPlanAprendizaje,
    SerializadorObjetivoPlanAprendizaje,
    SerializadorPlanEvaluacion,
    SerializadorItemPlanEvaluacion,
)
from autenticacion_docente.permissions import CedulaRequerida
from autenticacion_docente.models import Docente
from django.conf import settings

from django.shortcuts import get_object_or_404
from django.http import HttpResponse

# Vistas para PlanAprendizaje (limitadas por docente)
class CrearListarPlanAprendizaje(generics.ListCreateAPIView):
    """
    API endpoint para listar y crear Planes de Aprendizaje.
    Las operaciones están limitadas a los Planes de Aprendizaje asociados al docente autenticado.
    """
    serializer_class = SerializadorPlanAprendizaje
    permission_classes = [CedulaRequerida]

    def get_queryset(self):
        """
        Obtiene el conjunto de consultas de los Planes de Aprendizaje asociados al docente autenticado.
        """
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        return PlanAprendizaje.objects.filter(docente=docente)

    def perform_create(self, serializer):
        """
        Guarda una nueva instancia del Plan de Aprendizaje, asociándola al docente autenticado.
        """
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        serializer.save(docente=docente)

class ObtenerActualizarEliminarPlanAprendizaje(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint para obtener, actualizar y eliminar un Plan de Aprendizaje específico.
    Las operaciones están limitadas a los Planes de Aprendizaje asociados al docente autenticado.
    """
    serializer_class = SerializadorPlanAprendizaje
    permission_classes = [CedulaRequerida]

    def get_queryset(self):
        """
        Obtiene el conjunto de consultas de los Planes de Aprendizaje asociados al docente autenticado.
        """
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        return PlanAprendizaje.objects.filter(docente=docente)

class DescargarPlanAprendizaje(generics.GenericAPIView):
    """
    API endpoint para descargar un Plan de Aprendizaje específico en formato PDF.
    La descarga está limitada a los Planes de Aprendizaje asociados al docente autenticado.
    """
    permission_classes = [CedulaRequerida]

    def get(self, request, pk):
        """
        Genera y devuelve el PDF del Plan de Aprendizaje solicitado.
        """
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        codigo_grupo = pk
        pa = get_object_or_404(
            PlanAprendizaje,
            docente=docente,
            codigo_grupo=codigo_grupo
        )
        pdf_buffer = pa.generar_pdf()
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="plan_aprendizaje_{codigo_grupo}.pdf"'
        return response



# Vistas para ObjetivoPlanAprendizaje (limitadas por docente a través de PlanAprendizaje)
class CrearListarObjetivoPlanAprendizaje(generics.ListCreateAPIView):
    """
    API endpoint para listar y crear Objetivos de Plan de Aprendizaje.
    Las operaciones están limitadas a los Objetivos asociados a los Planes de Aprendizaje del docente autenticado.
    """
    serializer_class = SerializadorObjetivoPlanAprendizaje
    permission_classes = [CedulaRequerida]

    def get_queryset(self):
        """
        Obtiene el conjunto de consultas de los Objetivos de Plan de Aprendizaje
        asociados a los Planes de Aprendizaje del docente autenticado, ordenados por ID.
        """
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCente)
        docente = Docente.objects.get(cedula=cedula)
        return ObjetivoPlanAprendizaje.objects.filter(plan_aprendizaje__docente=docente).order_by('id')

class ObtenerActualizarEliminarObjetivoPlanAprendizaje(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint para obtener, actualizar y eliminar un Objetivo de Plan de Aprendizaje específico.
    Las operaciones están limitadas a los Objetivos asociados a los Planes de Aprendizaje del docente autenticado.
    """
    serializer_class = SerializadorObjetivoPlanAprendizaje
    permission_classes = [CedulaRequerida]

    def get_queryset(self):
        """
        Obtiene el conjunto de consultas de los Objetivos de Plan de Aprendizaje
        asociados a los Planes de Aprendizaje del docente autenticado.
        """
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        return ObjetivoPlanAprendizaje.objects.filter(plan_aprendizaje__docente=docente)

    def update(self, request, *args, **kwargs):
        """
        Actualiza un Objetivo de Plan de Aprendizaje específico, permitiendo la actualización
        del campo 'evaluacion_asociada'.
        """
        evaluacion_asociada = request.data.get('evaluacion_asociada')
        request.data['evaluacion_asociada'] = evaluacion_asociada
        return super().update(request, *args, **kwargs)

# Vistas para PlanEvaluacion (limitadas por docente a través de PlanAprendizaje)
class CrearListarPlanEvaluacion(generics.ListCreateAPIView):
    """
    API endpoint para listar y crear Planes de Evaluación.
    Las operaciones están limitadas a los Planes de Evaluación asociados a los Planes de Aprendizaje del docente autenticado.
    """
    serializer_class = SerializadorPlanEvaluacion
    permission_classes = [CedulaRequerida]

    def get_queryset(self):
        """
        Obtiene el conjunto de consultas de los Planes de Evaluación
        asociados a los Planes de Aprendizaje del docente autenticado.
        """
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        return PlanEvaluacion.objects.filter(plan_aprendizaje__docente=docente)

class ObtenerActualizarEliminarPlanEvaluacion(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint para obtener, actualizar y eliminar un Plan de Evaluación específico.
    Las operaciones están limitadas a los Planes de Evaluación asociados a los Planes de Aprendizaje del docente autenticado.
    """
    serializer_class = SerializadorPlanEvaluacion
    permission_classes = [CedulaRequerida]

    def get_queryset(self):
        """
        Obtiene el conjunto de consultas de los Planes de Evaluación
        asociados a los Planes de Aprendizaje del docente autenticado.
        """
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        return PlanEvaluacion.objects.filter(plan_aprendizaje__docente=docente)

class DescargarPlanEvaluacion(generics.GenericAPIView):
    """
    API endpoint para descargar un Plan de Evaluación específico en formato PDF.
    La descarga está limitada a los Planes de Evaluación asociados a los Planes de Aprendizaje del docente autenticado.
    """
    permission_classes = [CedulaRequerida]

    def get(self, request, pk):
        """
        Genera y devuelve el PDF del Plan de Evaluación solicitado.
        """
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        _id = pk
        pe = get_object_or_404(
            PlanEvaluacion,
            plan_aprendizaje__docente=docente,
            id=_id
        )
        pdf_buffer = pe.generar_pdf()
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{pe.nombre}.pdf"'
        return response


# Vistas para ItemPlanEvaluacion (limitadas por docente a través de PlanEvaluacion)
class CrearListarItemPlanEvaluacion(generics.ListCreateAPIView):
    """
    API endpoint para listar y crear Ítems de Plan de Evaluación.
    Las operaciones están limitadas a los Ítems asociados a los Planes de Evaluación del docente autenticado.
    """
    serializer_class = SerializadorItemPlanEvaluacion
    permission_classes = [CedulaRequerida]

    def get_queryset(self):
        """
        Obtiene el conjunto de consultas de los Ítems de Plan de Evaluación
        asociados a los Planes de Evaluación del docente autenticado.
        Permite filtrar por el ID del Plan de Evaluación ('pe' en los parámetros de la URL).
        """
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        pe_pk = self.request.GET.get('pe', None)
        queryset = ItemPlanEvaluacion.objects.filter(
            plan_evaluacion__plan_aprendizaje__docente=docente,
        )
        if pe_pk:
            queryset = queryset.filter(
                plan_evaluacion__pk=pe_pk
            )
        return queryset


class ObtenerActualizarEliminarItemPlanEvaluacion(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint para obtener, actualizar y eliminar un Ítem de Plan de Evaluación específico.
    Las operaciones están limitadas a los Ítems asociados a los Planes de Evaluación del docente autenticado.
    """
    serializer_class = SerializadorItemPlanEvaluacion
    permission_classes = [CedulaRequerida]

    def get_queryset(self):
        """
        Obtiene el conjunto de consultas de los Ítems de Plan de Evaluación
        asociados a los Planes de Evaluación del docente autenticado.
        """
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        return ItemPlanEvaluacion.objects.filter(plan_evaluacion__plan_aprendizaje__docente=docente)


#Vistas para Unidad Curricular
class CrearListarUnidadCurricular(generics.ListCreateAPIView):
    """
    API endpoint para listar y crear Unidades Curriculares.
    No requiere autenticación de docente específica para estas operaciones.
    """
    queryset = UnidadCurricular.objects.all()
    serializer_class = SerializadorUnidadCurricular

class ObtenerActualizarEliminarUnidadCurricular(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint para obtener, actualizar y eliminar una Unidad Curricular específica.
    No requiere autenticación de docente específica para estas operaciones.
    """
    queryset = UnidadCurricular.objects.all()
    serializer_class = SerializadorUnidadCurricular