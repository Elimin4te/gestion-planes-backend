from rest_framework import generics
from rest_framework.serializers import ValidationError

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
    serializer_class = SerializadorPlanAprendizaje
    permission_classes = [CedulaRequerida]

    def get_queryset(self):
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        return PlanAprendizaje.objects.filter(docente=docente)

    def perform_create(self, serializer):
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        serializer.save(docente=docente)

class ObtenerActualizarEliminarPlanAprendizaje(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SerializadorPlanAprendizaje
    permission_classes = [CedulaRequerida]

    def get_queryset(self):
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        return PlanAprendizaje.objects.filter(docente=docente)

class DescargarPlanAprendizaje(generics.GenericAPIView):
    permission_classes = [CedulaRequerida]

    def get(self, request, pk):
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
    serializer_class = SerializadorObjetivoPlanAprendizaje
    permission_classes = [CedulaRequerida]

    def get_queryset(self):
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        return ObjetivoPlanAprendizaje.objects.filter(plan_aprendizaje__docente=docente)

class ObtenerActualizarEliminarObjetivoPlanAprendizaje(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SerializadorObjetivoPlanAprendizaje
    permission_classes = [CedulaRequerida]

    def get_queryset(self):
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        return ObjetivoPlanAprendizaje.objects.filter(plan_aprendizaje__docente=docente)



# Vistas para PlanEvaluacion (limitadas por docente a través de PlanAprendizaje)
class CrearListarPlanEvaluacion(generics.ListCreateAPIView):
    serializer_class = SerializadorPlanEvaluacion
    permission_classes = [CedulaRequerida]

    def get_queryset(self):
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        return PlanEvaluacion.objects.filter(plan_aprendizaje__docente=docente)

class ObtenerActualizarEliminarPlanEvaluacion(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SerializadorPlanEvaluacion
    permission_classes = [CedulaRequerida]

    def get_queryset(self):
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        return PlanEvaluacion.objects.filter(plan_aprendizaje__docente=docente)

class DescargarPlanEvaluacion(generics.GenericAPIView):
    permission_classes = [CedulaRequerida]

    def get(self, request, pk):

        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        _id = pk
        pe = get_object_or_404(
            PlanEvaluacion, 
            plan_aprendizaje__docente=docente, 
            id=_id
        )

        # Valida que el peso sea justamente 100% para descargar
        if pe.suma_de_pesos_evaluaciones != 100:
            raise ValidationError(
                {'suma_de_pesos': f'Las evaluaciones del plan de evaluación no suman el 100% ({pe.suma_de_pesos_evaluaciones}%)'}
            )

        # Valida los items sin objetivos asociados
        items_sin_objetivos = []
        for item in pe.itemplanevaluacion_set.all():
            item: ItemPlanEvaluacion
            if len(item.objetivos) == 0:
                items_sin_objetivos.append(
                    f"{item.get_instrumento_evaluacion_display()} ({item.peso})%"
                )

        if len(items_sin_objetivos) > 0:
            raise ValidationError(
                {'items_sin_objetivo': f'Hay evaluaciones sin objetivos asociados: {", ".join(items_sin_objetivos)}'}
            )

        pdf_buffer = pe.generar_pdf()
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={pe.nombre}.pdf"'
        return response


# Vistas para ItemPlanEvaluacion (limitadas por docente a través de PlanEvaluacion)
class CrearListarItemPlanEvaluacion(generics.ListCreateAPIView):
    serializer_class = SerializadorItemPlanEvaluacion
    permission_classes = [CedulaRequerida]

    def get_queryset(self):
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        return ItemPlanEvaluacion.objects.filter(plan_evaluacion__plan_aprendizaje__docente=docente)

class ObtenerActualizarEliminarItemPlanEvaluacion(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SerializadorItemPlanEvaluacion
    permission_classes = [CedulaRequerida]

    def get_queryset(self):
        cedula = self.request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        return ItemPlanEvaluacion.objects.filter(plan_evaluacion__plan_aprendizaje__docente=docente)



#Vistas para Unidad Curricular
class CrearListarUnidadCurricular(generics.ListCreateAPIView):
    queryset = UnidadCurricular.objects.all()
    serializer_class = SerializadorUnidadCurricular

class ObtenerActualizarEliminarUnidadCurricular(generics.RetrieveUpdateDestroyAPIView):
    queryset = UnidadCurricular.objects.all()
    serializer_class = SerializadorUnidadCurricular