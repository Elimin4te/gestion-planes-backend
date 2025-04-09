from rest_framework import serializers
from .models import (
    UnidadCurricular,
    PlanAprendizaje,
    ObjetivoPlanAprendizaje,
    PlanEvaluacion,
    ItemPlanEvaluacion,
)
from autenticacion_docente.models import Docente

from django.utils.timezone import now


class SerializadorDocente(serializers.ModelSerializer):
    """
    Serializador para el modelo Docente.
    Incluye todos los campos del modelo.
    """
    class Meta:
        model = Docente
        fields = '__all__'


class SerializadorUnidadCurricular(serializers.ModelSerializer):
    """
    Serializador para el modelo UnidadCurricular.
    Incluye todos los campos del modelo.
    """
    class Meta:
        model = UnidadCurricular
        fields = '__all__'


class SerializadorObjetivoPlanAprendizaje(serializers.ModelSerializer):
    """
    Serializador para el modelo ObjetivoPlanAprendizaje.
    Incluye todos los campos del modelo.

    Sobreescribe los métodos `create` y `update` para actualizar
    la fecha de modificación del Plan de Aprendizaje asociado.
    """
    class Meta:
        model = ObjetivoPlanAprendizaje
        fields = '__all__'

    # Se sobrecargan los metodos de create y update para que se modifique la fecha de modificacion del Plan.

    def create(self, validated_data):
        """
        Crea un nuevo Objetivo de Plan de Aprendizaje y actualiza la fecha de
        modificación del Plan de Aprendizaje asociado.

        Args:
            validated_data (dict): Datos validados para la creación del objetivo.

        Returns:
            ObjetivoPlanAprendizaje: La instancia del objetivo creada.
        """
        pa: PlanAprendizaje = validated_data['plan_aprendizaje']
        pa.fecha_modificacion = now()
        pa.save()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Actualiza un Objetivo de Plan de Aprendizaje existente y actualiza la fecha de
        modificación del Plan de Aprendizaje asociado.

        Args:
            instance (ObjetivoPlanAprendizaje): La instancia del objetivo a actualizar.
            validated_data (dict): Datos validados para la actualización del objetivo.

        Returns:
            ObjetivoPlanAprendizaje: La instancia del objetivo actualizada.
        """
        pa: PlanAprendizaje = validated_data['plan_aprendizaje']
        pa.fecha_modificacion = now()
        pa.save()
        return super().update(instance, validated_data)


class SerializadorPlanAprendizaje(serializers.ModelSerializer):
    """
    Serializador para el modelo PlanAprendizaje.
    Incluye todos los campos del modelo y relaciones con Docente y UnidadCurricular.

    Incluye un campo de solo lectura para los objetivos asociados y un campo
    para obtener el ID del Plan de Evaluación asociado.
    """
    docente = serializers.PrimaryKeyRelatedField(queryset=Docente.objects.all())
    unidad_curricular = serializers.PrimaryKeyRelatedField(queryset=UnidadCurricular.objects.all())
    objetivos_plan_aprendizaje = SerializadorObjetivoPlanAprendizaje(many=True, read_only=True, source='objetivoplanaprendizaje_set')
    plan_evaluacion = serializers.SerializerMethodField("get_plan_evaluacion")

    class Meta:
        model = PlanAprendizaje
        fields = '__all__'

    def get_plan_evaluacion(self, instancia: PlanAprendizaje) -> int | None:
        """
        Obtiene el ID del Plan de Evaluación asociado a este Plan de Aprendizaje.

        Args:
            instancia (PlanAprendizaje): La instancia del Plan de Aprendizaje.

        Returns:
            int | None: El ID del Plan de Evaluación si existe, None en caso contrario.
        """
        try:
            return PlanEvaluacion.objects.get(plan_aprendizaje=instancia).pk
        except PlanEvaluacion.DoesNotExist:
            pass


class SerializadorItemPlanEvaluacion(serializers.ModelSerializer):
    """
    Serializador para el modelo ItemPlanEvaluacion.
    Incluye todos los campos del modelo y una relación de solo lectura con los objetivos asociados.

    Sobreescribe los métodos `create` y `update` para actualizar
    la fecha de modificación del Plan de Evaluación asociado y validar
    que el porcentaje total de los ítems no supere el 100%.
    """
    objetivos = SerializadorObjetivoPlanAprendizaje(many=True, read_only=True, source='objetivos_asociados')
    class Meta:
        model = ItemPlanEvaluacion
        fields = '__all__'

    # Se sobrecargan los metodos de create y update para que se modifique la fecha de modificacion del Plan
    # y para validar que el porcentaje total del mismo no supere el limite de 100%.

    def create(self, validated_data):
        """
        Crea un nuevo Ítem de Plan de Evaluación, actualiza la fecha de
        modificación del Plan de Evaluación asociado y valida que el peso total
        de los ítems no exceda el 100%.

        Args:
            validated_data (dict): Datos validados para la creación del ítem.

        Returns:
            ItemPlanEvaluacion: La instancia del ítem creada.

        Raises:
            serializers.ValidationError: Si al crear el ítem se supera el 100% del peso total.
        """
        pe: PlanEvaluacion = validated_data['plan_evaluacion']
        peso: int = validated_data['peso']
        total_teorico = pe.peso_total + peso
        if total_teorico > 100:
            peso_disponible = 100 - pe.peso_total
            complemento = f"Actualmente queda un {peso_disponible}% por asignar." if peso_disponible > 0 else ''
            raise serializers.ValidationError(
                f"No se puede crear un nuevo item con peso {peso}% ya que se superaría el límite de 100% para un plan de evaluación ({total_teorico}%).{complemento}"
            )
        pe.fecha_modificacion = now()
        pe.save()
        return super().create(validated_data)

    def update(self, instance: ItemPlanEvaluacion, validated_data):
        """
        Actualiza un Ítem de Plan de Evaluación existente, actualiza la fecha de
        modificación del Plan de Evaluación asociado y valida que el peso total
        de los ítems no exceda el 100%.

        Args:
            instance (ItemPlanEvaluacion): La instancia del ítem a actualizar.
            validated_data (dict): Datos validados para la actualización del ítem.

        Returns:
            ItemPlanEvaluacion: La instancia del ítem actualizada.

        Raises:
            serializers.ValidationError: Si al actualizar el ítem se supera el 100% del peso total.
        """
        pe: PlanEvaluacion = validated_data['plan_evaluacion']
        peso: int = validated_data['peso']
        nuevo_total_teorico = (pe.peso_total + peso) - instance.peso
        if nuevo_total_teorico > 100:
            raise serializers.ValidationError(
                f"No se puede actualizar este item con peso {peso}% ya que se superaría el límite de 100% para un plan de evaluación ({nuevo_total_teorico}%)."
            )
        pe.fecha_modificacion = now()
        pe.save()
        return super().update(instance, validated_data)


class SerializadorPlanEvaluacion(serializers.ModelSerializer):
    """
    Serializador para el modelo PlanEvaluacion.
    Incluye todos los campos del modelo, una relación con el Plan de Aprendizaje
    y un campo de solo lectura para los ítems asociados.

    Incluye un campo para mostrar el peso total actual de los ítems
    y sobreescribe el método `create` para validar que no exista
    ya un Plan de Evaluación asociado al Plan de Aprendizaje.
    """
    plan_aprendizaje = serializers.PrimaryKeyRelatedField(queryset=PlanAprendizaje.objects.all())
    items_plan_evaluacion = SerializadorItemPlanEvaluacion(many=True, read_only=True, source='itemplanevaluacion_set')
    peso_total_actual = serializers.SerializerMethodField('obtener_peso_total')

    class Meta:
        model = PlanEvaluacion
        fields = '__all__'

    def obtener_peso_total(self, instancia: PlanEvaluacion) -> str:
        """
        Obtiene el peso total actual de los ítems asociados al Plan de Evaluación
        y lo formatea como una cadena con el símbolo de porcentaje.

        Args:
            instancia (PlanEvaluacion): La instancia del Plan de Evaluación.

        Returns:
            str: El peso total actual formateado (ej: "85%").
        """
        return str(instancia.peso_total) + '%'

    def create(self, validated_data):
        """
        Crea un nuevo Plan de Evaluación y valida que no exista ya un Plan de
        Evaluación asociado al Plan de Aprendizaje proporcionado.

        Args:
            validated_data (dict): Datos validados para la creación del plan de evaluación.

        Returns:
            PlanEvaluacion: La instancia del plan de evaluación creada.

        Raises:
            serializers.ValidationError: Si ya existe un Plan de Evaluación asociado al Plan de Aprendizaje.
        """
        pa: PlanAprendizaje = validated_data['plan_aprendizaje']
        if PlanEvaluacion.objects.filter(plan_aprendizaje=pa).exists():
            raise serializers.ValidationError(
                f"Ya existe un plan de evaluación asociado al plan de aprendizaje ({pa.codigo_grupo})"
            )
        return super().create(validated_data)