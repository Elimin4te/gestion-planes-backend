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
    docente = serializers.PrimaryKeyRelatedField(queryset=Docente.objects.all())
    unidad_curricular = serializers.PrimaryKeyRelatedField(queryset=UnidadCurricular.objects.all())
    objetivos_plan_aprendizaje = SerializadorObjetivoPlanAprendizaje(many=True, read_only=True, source='objetivoplanaprendizaje_set')

    class Meta:
        model = PlanAprendizaje
        fields = '__all__'


class SerializadorItemPlanEvaluacion(serializers.ModelSerializer):
    objetivos_asociados = SerializadorObjetivoPlanAprendizaje(many=True, read_only=True, source='objetivoplanaprendizaje_set')
    class Meta:
        model = ItemPlanEvaluacion
        fields = '__all__'


class SerializadorPlanEvaluacion(serializers.ModelSerializer):
    plan_aprendizaje = serializers.PrimaryKeyRelatedField(queryset=PlanAprendizaje.objects.all())
    items_plan_evaluacion = SerializadorItemPlanEvaluacion(many=True, read_only=True, source='itemplanevaluacion_set')

    class Meta:
        model = PlanEvaluacion
        fields = '__all__'