from rest_framework import serializers
from autenticacion_docente.models import Docente
from django.core.validators import RegexValidator


class SerializadorInicioSesion(serializers.Serializer):
    """Serializador para validar los datos enviados para autenticación del docente."""
    cedula = serializers.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^[V]-\d{7,8}$",
                message="Ingrese una cédula venezolana válida (Ej: V-12345678)",
                code="cedula_invalida"
            )   
        ]
    )

    docente = None  # Atributo para almacenar el docente para evitar reprocesamiento

    def validate(self, data):
        """Valida la cédula y verifica si el docente existe."""
        cedula = data['cedula']
        try:
            self.docente = Docente.objects.get(cedula=cedula)
        except Docente.DoesNotExist:
            raise serializers.ValidationError("No existe un docente con esa cédula.")
        return data


class SerializadorDocente(serializers.ModelSerializer):
    """Serializador para respuestas JSON."""
    class Meta:
        model = Docente
        fields = '__all__'  # Incluye todos los campos del modelo