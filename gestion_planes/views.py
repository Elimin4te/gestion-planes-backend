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