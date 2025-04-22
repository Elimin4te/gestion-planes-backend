from rest_framework import serializers
from autenticacion_docente.models import Docente, NUMERO_MINIMO_CEDULA, NUMERO_MAXIMO_CEDULA, MENSAJE_CEDULA_INVALIDA
from django.core.validators import MinValueValidator, MaxValueValidator


class SerializadorInicioSesion(serializers.Serializer):
    """
    Serializador para validar los datos de inicio de sesión de un docente.

    Atributos:
        cedula (serializers.CharField): Campo para la cédula del docente.

        docente (Docente | None): Atributo para almacenar la instancia del
            Docente recuperada durante la validación. Inicialmente es None.
    """
    cedula = serializers.IntegerField(
        validators=[
            MinValueValidator(NUMERO_MINIMO_CEDULA, MENSAJE_CEDULA_INVALIDA),
            MaxValueValidator(NUMERO_MAXIMO_CEDULA, MENSAJE_CEDULA_INVALIDA)
        ],
        error_messages={
            'blank': 'La cédula es requerida.'
        }
    )

    docente = None  # Atributo para almacenar el docente para evitar reprocesamiento

    def validate(self, data):
        """
        Valida los datos de inicio de sesión.

        Verifica que la cédula cumpla con el formato venezolano y que exista
        un docente registrado con esa cédula en la base de datos.

        Args:
            data (dict): Diccionario con los datos a validar (en este caso, solo 'cedula').

        Returns:
            dict: Los datos validados si la cédula es válida y el docente existe.

        Raises:
            serializers.ValidationError: Si la cédula no tiene el formato correcto
                o si no se encuentra ningún docente con la cédula proporcionada.
        """
        cedula = data['cedula']
        try:
            self.docente = Docente.objects.get(cedula=cedula)
        except Docente.DoesNotExist:
            raise serializers.ValidationError("No existe un docente con esa cédula.", code='docente_no_existe')
        return data


class SerializadorDocente(serializers.ModelSerializer):
    """
    Serializador para el modelo Docente, utilizado para la representación JSON
    de la información del docente en las respuestas de la API.

    Meta:
        model (Docente): Especifica el modelo Django al que este serializador está asociado.
        fields (str): Define qué campos del modelo se incluirán en la serialización.
            '__all__' indica que se deben incluir todos los campos del modelo.
    """
    class Meta:
        model = Docente
        fields = '__all__'  # Incluye todos los campos del modelo