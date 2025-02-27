from rest_framework import serializers
from .models import (
    UnidadCurricular,
    PlanAprendizaje,
    ObjetivoPlanAprendizaje,
    PlanEvaluacion,
    ItemPlanEvaluacion,
)
from autenticacion_docente.models import Docente


class SerializadorDocente(serializers.ModelSerializer):
    class Meta:
        model = Docente
        fields = '__all__'


class SerializadorUnidadCurricular(serializers.ModelSerializer):
    class Meta:
        model = UnidadCurricular
        fields = '__all__'


class SerializadorObjetivoPlanAprendizaje(serializers.ModelSerializer):
    class Meta:
        model = ObjetivoPlanAprendizaje
        fields = '__all__'


class SerializadorPlanAprendizaje(serializers.ModelSerializer):
    docente = SerializadorDocente(read_only=True)
    unidad_curricular = SerializadorUnidadCurricular(read_only=True)
    objetivos_plan_aprendizaje = SerializadorObjetivoPlanAprendizaje(many=True, read_only=True, source='objetivoplanaprendizaje_set')

    class Meta:
        model = PlanAprendizaje
        fields = '__all__'


class SerializadorItemPlanEvaluacion(serializers.ModelSerializer):
    objetivo_asociado = SerializadorObjetivoPlanAprendizaje(read_only=True)

    class Meta:
        model = ItemPlanEvaluacion
        fields = '__all__'


class SerializadorPlanEvaluacion(serializers.ModelSerializer):
    plan_aprendizaje = SerializadorPlanAprendizaje(read_only=True)
    items_plan_evaluacion = SerializadorItemPlanEvaluacion(many=True, read_only=True, source='itemplanevaluacion_set')

    class Meta:
        model = PlanEvaluacion
        fields = '__all__'