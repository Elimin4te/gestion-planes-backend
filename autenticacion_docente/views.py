from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse

from autenticacion_docente.serializers import SerializadorDocente, SerializadorInicioSesion
from autenticacion_docente.permissions import CedulaRequerida
from autenticacion_docente.models import Docente

from django.conf import settings


class IniciarSesion(APIView):
    """
    API endpoint para la autenticación de docentes.

    Permite a un docente iniciar sesión proporcionando su cédula.
    Tras una autenticación exitosa, la cédula del docente se guarda
    en una cookie en la respuesta.
    """
    permission_classes = [AllowAny]
    serializer_class = SerializadorInicioSesion

    @extend_schema(
        summary="Iniciar sesión de docente",
        description="Autentica a un docente y guarda su cédula en una cookie.",
        request=SerializadorInicioSesion,
        responses={
            202: OpenApiResponse(description="Inicio de sesión exitoso. Cookie configurada."),
            400: OpenApiResponse(description="Solicitud incorrecta. Errores en los datos enviados."),
        }
    )
    def post(self, request):
        """
        Maneja la solicitud POST para iniciar sesión.

        Valida los datos de la solicitud utilizando el SerializadorInicioSesion.
        Si la validación es exitosa, guarda la cédula del docente en una cookie
        y devuelve una respuesta 202. Si la validación falla, devuelve
        una respuesta 400 con los errores de validación.
        """
        serializador = SerializadorInicioSesion(data=request.data)
        if serializador.is_valid():

            # Guardar la cedula en una cookie
            response = Response(status=202)
            response.set_cookie(settings.NOMBRE_COOKIE_DOCENTE, serializador.docente.cedula, httponly=True)

            return response

        else:
            # Devuelve la respuesta con los errores detectados.
            return Response(serializador.errors, status=400)


class ObtenerDatosDocente(APIView):
    """
    API endpoint para obtener los datos del docente autenticado.

    Requiere que el docente esté autenticado (la cookie de cédula sea válida).
    Devuelve la información del docente en formato JSON.
    """
    permission_classes = [CedulaRequerida]

    @extend_schema(
        summary="Obtener datos del docente",
        description="Obtiene los datos del docente autenticado a través de la cookie.",
        responses={
            200: SerializadorDocente,
            403: OpenApiResponse(description="No autenticado. Cookie de cédula no encontrada o inválida."),
        }
    )
    def get(self, request):
        """
        Maneja la solicitud GET para obtener los datos del docente.

        Recupera la cédula del docente de la cookie y busca al docente
        correspondiente en la base de datos. Serializa los datos del docente
        utilizando el SerializadorDocente y los devuelve en la respuesta.
        """
        cedula: str = request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        docente = SerializadorDocente(docente)
        return Response(docente.data)


class CerrarSesion(APIView):
    """
    API endpoint para cerrar la sesión del docente.

    Requiere que el docente esté autenticado (la cookie de cédula sea válida).
    Elimina la cookie de cédula del navegador del cliente.
    """
    permission_classes = [CedulaRequerida]

    @extend_schema(
        summary="Cerrar sesión de docente",
        description="Elimina la cookie de cédula del docente para cerrar la sesión.",
        responses={
            202: OpenApiResponse(description="Cierre de sesión exitoso. Cookie eliminada."),
            403: OpenApiResponse(description="No autenticado. Cookie de cédula no encontrada o inválida."),
        }
    )
    def get(self, request):
        """
        Maneja la solicitud GET para cerrar sesión.

        Crea una respuesta 202 (Éxito) y elimina la cookie que contiene
        la cédula del docente.
        """
        response = Response(status=202)
        response.delete_cookie(settings.NOMBRE_COOKIE_DOCENTE)
        return response


class RegistroDocente(CreateAPIView):
    """
    API endpoint para registrar un nuevo docente.

    Permite la creación de nuevas cuentas de docente en el sistema.
    Utiliza el SerializadorDocente para la validación y creación de los datos.
    """
    serializer_class = SerializadorDocente