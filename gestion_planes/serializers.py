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
    unidad_curricular = serializers.PrimaryKeyRelatedField(queryset=UnidadCurricular.objects.all())
    objetivos_plan_aprendizaje = SerializadorObjetivoPlanAprendizaje(many=True, required=False, source='objetivoplanaprendizaje_set')
    fecha_creacion = serializers.DateTimeField(read_only=True)
    fecha_modificacion = serializers.DateTimeField(read_only=True)

    class Meta:
        model = PlanAprendizaje
        fields = '__all__'


class SerializadorItemPlanEvaluacion(serializers.ModelSerializer):
    objetivos = SerializadorObjetivoPlanAprendizaje(many=True, required=False, source='objetivos_asociados')
    class Meta:
        model = ItemPlanEvaluacion
        fields = '__all__'

    def validate(self, attrs):
        instance = ItemPlanEvaluacion(**attrs)
        instance.full_clean()
        return super().validate(attrs)


class SerializadorPlanEvaluacion(serializers.ModelSerializer):
    plan_aprendizaje = serializers.PrimaryKeyRelatedField(queryset=PlanAprendizaje.objects.all())
    items_plan_evaluacion = SerializadorItemPlanEvaluacion(many=True, required=False, source='itemplanevaluacion_set')
    fecha_creacion = serializers.DateTimeField(read_only=True)
    fecha_modificacion = serializers.DateTimeField(read_only=True)

    class Meta:
        model = PlanEvaluacion
        fields = '__all__'