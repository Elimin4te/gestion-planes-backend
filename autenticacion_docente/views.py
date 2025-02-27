from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse

from autenticacion_docente.serializers import SerializadorDocente, SerializadorInicioSesion
from autenticacion_docente.permissions import CedulaRequerida
from autenticacion_docente.models import Docente

from django.conf import settings


class IniciarSesion(APIView):
    """Controlador para la autenticación docente."""
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
    """Controlador para mostrar datos de docente."""

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
        cedula: str = request.COOKIES.get(settings.NOMBRE_COOKIE_DOCENTE)
        docente = Docente.objects.get(cedula=cedula)
        docente = SerializadorDocente(docente)
        return Response(docente.data)


class CerrarSesion(APIView):
    """Controlador para eliminar cookie de docente."""

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
        response = Response(status=202)
        response.delete_cookie(settings.NOMBRE_COOKIE_DOCENTE)
        return response